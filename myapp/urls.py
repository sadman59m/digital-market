from django.urls import path
from . import views

app_name = 'myapp'

urlpatterns = [
    path('', views.index_view, name='index'),
    path('product/<int:id>', views.detail_view, name='detail'),
    path('api/checkout-session/<int:id>', views.create_checkout_session_view, name='api_checkout_session'),
    path('success', views.payment_success_view, name='success'),
    path('failed', views.payment_failed_view, name='failed'),
    path('create-product', views.create_product_view, name='createproduct'),
    path('update-product/<int:id>', views.update_product_view, name='updateproduct'),
    path('delete-product/<int:id>', views.delete_product_view, name='deleteproduct'),
    path('dashboard', views.dashboard_view, name='dashboard'),
    path('registration', views.user_registration_view, name='registration'),
    path('login', views.user_login_view, name='login'),
    path('logout', views.user_logout_view, name='logout'),
    path('purchases', views.purchases_view, name='purchases'),
    path('sales', views.sales_view, name='sales')
]