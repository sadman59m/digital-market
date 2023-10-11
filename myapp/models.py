from django.db import models
from django.contrib.auth.models import AbstractUser


# Create your models here.


class CustomUser(AbstractUser):
    email = models.EmailField(max_length=100, unique=True)

    USERNAME_FIELD = 'username'
    # set this for the required fields except the USERNAME_FIELD
    REQUIRED_FIELDS = ['email']


class Product(models.Model):
    class Meta:
        ordering = ["pk"]

    seller = models.ForeignKey(CustomUser, on_delete=models.CASCADE, default=1)
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=30, decimal_places=2)
    file = models.FileField(upload_to='uploads')
    total_sale_amount = models.DecimalField(max_digits=50, decimal_places=2, default=0.00)
    total_sale = models.IntegerField(default=0)

    def __str__(self):
        return f"id:{self.id} name:{self.name}"
    

class OrderDetail(models.Model):
    customer_email = models.EmailField()
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=30, decimal_places=2)
    stripe_session_id = models.CharField(max_length=300, default="")
    stripe_payment_intent = models.CharField(max_length=200, null=True)
    has_paid = models.BooleanField(default=False)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now_add=True)





