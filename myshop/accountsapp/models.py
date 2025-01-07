from django.contrib.auth.models import User
from django.db import models


class Profile(models.Model):
    """Модель профиля с данными пользователя"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    about = models.TextField(max_length=500, blank=True, null=True)

