# Generated by Django 5.1.4 on 2024-12-24 09:59

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shopapp', '0003_alter_order_options'),
    ]

    operations = [
        migrations.RenameField(
            model_name='order',
            old_name='user_id',
            new_name='user',
        ),
    ]
