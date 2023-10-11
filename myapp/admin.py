from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import CustomAdminUserForm
from .models import CustomUser, Product, OrderDetail

# Register your models here.

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    add_form  = CustomAdminUserForm

class ProductAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'description', 'price', 'file', 'seller']
    list_per_page = 5

class OrderDetailAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer_email', 'amount', 'has_paid']
    list_per_page = 5


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(OrderDetail, OrderDetailAdmin)