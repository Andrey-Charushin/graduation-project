# Generated by Django 5.1.4 on 2024-12-26 12:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shopapp', '0008_alter_review_product'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='reviews',
        ),
    ]
