# Generated by Django 5.1.4 on 2024-12-31 12:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shopapp', '0011_alter_review_options_cart_cartitem'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='delivery_address',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='payment_method',
            field=models.CharField(max_length=100, null=True),
        ),
    ]
