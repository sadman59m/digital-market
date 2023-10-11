from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
from django.http import JsonResponse, HttpResponseNotFound, Http404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
import stripe, json
import os
import datetime

from .models import Product, OrderDetail, CustomUser
from .forms import ProductForm, UserRegistrationForm, UserLoginForm
# Create your views here.

def index_view(request):
    products = Product.objects.all()
    return render(request, 'myapp/index.html', {"products": products})



def detail_view(request, id):
    product = Product.objects.get(id=id)
    stripe_publishable_key = settings.STRIPE_PUBLISHABLE_KEY
    return render(request, 'myapp/detail.html', {"product": product, "stripe_publishable_key": stripe_publishable_key})


@login_required(login_url='myapp:login')
@csrf_exempt
def create_checkout_session_view(request, id):
    # getting json data from AJAX request
    request_data = json.loads(request.body)
    if not 'email' in request_data:
        messages.info(request, "Please, Log in to continue")
        return redirect('myapp:login')

    product = Product.objects.get(id=id)
    stripe.api_key = settings.STRIPE_SECRET_KEY

    # create a stripe checkout session object
    try:
        checkout_session = stripe.checkout.Session.create(
            customer_email = request_data['email'],
            payment_method_types = ['card'],
            line_items = [
                {
                    'price_data':{
                        'currency': 'usd',
                        'product_data': {
                            'name': product.name
                        },
                        'unit_amount': int(product.price * 100)
                    },
                    'quantity': 1,
                }
            ],
            mode = 'payment',
            success_url = request.build_absolute_uri(reverse('myapp:success')) + 
            "?session_id={CHECKOUT_SESSION_ID}",
            cancel_url = request.build_absolute_uri(reverse('myapp:failed'))
        )

        # creating order instance and saving into db
        order = OrderDetail()
        order.customer_email = request_data['email']
        order.product = product
        order.amount = product.price
        order.stripe_session_id = checkout_session.id
        order.save()
        return JsonResponse({'sessionId': checkout_session.id})
    except:
        return JsonResponse({'error': 'Internal Error'}, status=500)


@login_required(login_url='myapp:login')
def payment_success_view(request):
    #get the sessionId form the successurl: ?session_id={CHECKOUT_SESSION_ID}
    session_id = request.GET.get('session_id')

    if session_id is None:
        return HttpResponseNotFound()
    
    # retrive the session info from stripe
    stripe.api_key = settings.STRIPE_SECRET_KEY
    try:
        session = stripe.checkout.Session.retrieve(session_id)
        order = get_object_or_404(OrderDetail, stripe_session_id=session.id)
        if session.payment_intent == None:
            raise Http404("Unauthorized access")
        order.stripe_payment_intent = session.payment_intent
        order.has_paid = True
        product = Product.objects.get(id=order.product.id)
        product.total_sale_amount = product.total_sale_amount + order.amount
        product.total_sale = product.total_sale + 1
        product.save()
        order.save()
        return render(request, 'myapp/payment_success.html', {"order": order})
    except:
        raise Http404("session id does not exist")



@login_required(login_url='myapp:login')
def payment_failed_view(request):
    return render(request, 'myapp/payment_failed.html')


@login_required(login_url='myapp:login')
def create_product_view(request):
    if request.method == 'POST':
        product_form = ProductForm(request.POST, request.FILES)
        
        if product_form.is_valid():
            new_product = product_form.save(commit=False)
            new_product.seller = request.user
            new_product.save()
            return redirect('myapp:dashboard')

    else:
        product_form = ProductForm()

    return render(request, 'myapp/create_product.html', {
        "product_form": product_form,
        "path": "/createproduct"
        })



@login_required(login_url='myapp:login')
def update_product_view(request, id):
    try:
        product = Product.objects.get(id=id)
        current_file_path = product.file.path
    except Exception as err:
        return Http404('product not found')

    if product.seller != request.user:
        messages.error(request, 'invalid request')
        return redirect('myapp:dashboard')

    if request.method == "POST":
        product_form = ProductForm(request.POST, request.FILES, instance=product)
        if product_form.is_valid():
            if request.FILES:
                if os.path.exists(current_file_path):
                    os.remove(current_file_path)
            new_product_fomr = product_form.save()
            return redirect('myapp:dashboard')
    else:
        product_form = ProductForm(instance=product)

    return render(request, 'myapp/create_product.html', {
        "product_form": product_form,
        "product": product,
        "update": True
    })





@login_required(login_url='myapp:login')
def delete_product_view(request, id):
    try:
        product = Product.objects.get(id=id)

        if product.seller != request.user:
            messages.error(request, 'invalid request')
            return redirect('myapp:dashboard')

        if request.method == "POST":
                if product.file:
                    file_path = product.file.path
                    if os.path.exists(file_path):
                        os.remove(file_path)
                product.delete()
                return redirect(reverse("myapp:dashboard"))

        return render(request, 'myapp/delete_product.html', { "product": product})
    except:
        raise Http404('Product Id does not exist')





@login_required(login_url='myapp:login')
def dashboard_view(request):
    products = Product.objects.filter(seller=request.user)
    return render(request, 'myapp/dashboard.html', {"products": products, "path": "/dashboard"})





def user_registration_view(request):
    if request.method == "POST":
        registration_form = UserRegistrationForm(request.POST)

        if registration_form.is_valid():
            new_user = registration_form.save()
            return redirect('myapp:dashboard')
    else:
        registration_form = UserRegistrationForm()

    return render(request, 'myapp/registration_form.html', {"form": registration_form, "path": "/register"})



def user_login_view(request):
    if request.method == 'POST':
        form_data = UserLoginForm(request.POST)

        if form_data.is_valid():
            email = form_data.cleaned_data['email']
            password = form_data.cleaned_data['password']
            user_info = CustomUser.objects.get(email=email)
            valid_user = authenticate(request, username=user_info.username, password=password)
            if valid_user is not None:
                login(request, valid_user)
                return redirect('myapp:dashboard')
            else:
                return render(request, 'myapp/login_form.html', {"form": form_data, "error": True})
    else:
        form_data = UserLoginForm()
    if 'next' in request.GET:
        print(request.GET['next'])
        messages.info(request, 'Please, log in to continue')
    return render(request, 'myapp/login_form.html', {"form": form_data, "path": '/login'})


def user_logout_view(request):
    logout(request)
    return redirect('myapp:index')





@login_required(login_url='myapp:login')
def purchases_view(request):
    print(request.user.email)
    orders = OrderDetail.objects.filter(has_paid=True, customer_email=request.user.email)
    return render(request, 'myapp/purchases.html',
    {"orders": orders, "path": "/purchases"})



@login_required(login_url='myapp:sales')
def sales_view(request):
    orders = OrderDetail.objects.filter(product__seller = request.user, has_paid=True)
    total_sales = orders.aggregate(Sum('amount'))
    print(total_sales)

    # last 365 days
    last_year = datetime.date.today() - datetime.timedelta(days=365)
    last_year_sales = OrderDetail.objects.filter(product__seller = request.user, has_paid = True, updated_on__gt=last_year)
    last_year_sales_amount = last_year_sales.aggregate(Sum('amount'))

    # last 30 days
    last_month = datetime.date.today() - datetime.timedelta(days=30)
    last_month_sales = OrderDetail.objects.filter(product__seller = request.user, has_paid = True, updated_on__gt=last_month)
    last_month_amount = last_month_sales.aggregate(Sum('amount'))

    # last year sales
    last_week = datetime.date.today() - datetime.timedelta(days=7)
    last_week_sales = OrderDetail.objects.filter(product__seller = request.user, has_paid = True, updated_on__gt=last_week)
    last_week_sales_amount = last_week_sales.aggregate(Sum('amount'))

    # 30 day sales by day
    # daily_sales_sum = OrderDetail.objects.filter(product__seller=request.user, has_paid=True, updated_on__gt=last_month)
    # .values('updated_on__date').order_by('updated_on__date').annotate(sum=Sum('amount'))
  
    # print(daily_sales_sum)
    last_month_daily = OrderDetail.objects.filter(product__seller = request.user, has_paid = True, updated_on__gt=last_month)
    last_month_daily_sales = last_month_daily.values('updated_on__date').order_by('updated_on__date').annotate(sum=Sum('amount'))

    last_month_daily = OrderDetail.objects.filter(product__seller = request.user, has_paid = True, updated_on__gt=last_month)
    last_month_product_sales = last_month_daily.values('product__name').order_by('product__name').annotate(sum=Sum('amount'))


    return render(request, 'myapp/sales.html',{
            'total_sales': total_sales,
            'last_year_sales': last_year_sales_amount,
            'last_month_sales': last_month_amount,
            'last_week_sales': last_week_sales_amount,
            'last_month_daily_sales': last_month_daily_sales,
            'last_month_product_sales': last_month_product_sales
            })