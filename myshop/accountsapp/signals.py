from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from shopapp.models import Cart

@receiver(post_save, sender=User)
def create_user_cart(sender, instance, created, **kwargs):
    """Создание корзины при регистрации пользователя"""
    if created:
        Cart.objects.create(user=instance)