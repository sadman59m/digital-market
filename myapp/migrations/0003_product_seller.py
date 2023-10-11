# Generated by Django 4.2.5 on 2023-10-10 17:52

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("myapp", "0002_remove_customuser_is_buyer_alter_customuser_email"),
    ]

    operations = [
        migrations.AddField(
            model_name="product",
            name="seller",
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
