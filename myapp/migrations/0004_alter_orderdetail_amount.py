# Generated by Django 4.2.5 on 2023-10-11 05:26

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("myapp", "0003_product_seller"),
    ]

    operations = [
        migrations.AlterField(
            model_name="orderdetail",
            name="amount",
            field=models.DecimalField(decimal_places=2, max_digits=30),
        ),
    ]
