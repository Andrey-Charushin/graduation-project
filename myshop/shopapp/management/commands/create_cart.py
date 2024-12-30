from django.contrib.auth.models import User
from django.core.management import BaseCommand
from django.db import transaction
from shopapp.models import Cart, Product


class Command(BaseCommand):
    @transaction.atomic
    def handle(self, *args, **options):
        user = User.objects.get(username="Andrey")
        self.stdout.write(f"Create cart for user {user}")
        cart, created = Cart.objects.get_or_create(
            user=user,
        )

        cart.save()
        self.stdout.write(f"Created cart {cart}")
