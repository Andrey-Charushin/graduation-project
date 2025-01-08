from django.db import models
from django.contrib.auth.models import User
from django.db.models import Avg


class Category(models.Model):
    """Модель для категории товаров"""

    class Meta:
        ordering = ["name", ]
        verbose_name_plural = 'categories'

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    """Модель для продукта"""

    class Meta:
        ordering = ["name", "price"]
        verbose_name_plural = 'products'

    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to='products/', null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def is_in_stock(self):
        """Проверка наличия товара на складе"""
        return self.stock > 0

    def average_rating(self):
        """Вычисляет средний рейтинг для продукта на основе отзвов пользователей"""
        avg_rating = self.review.aggregate(average=Avg('rating'))['average']
        return round(avg_rating, 2) if avg_rating else "Нет отзывов"


class Cart(models.Model):
    """Модель корзины"""

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="cart")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cart of {self.user.username}"

    def get_total(self):
        """Вычисление общей стоимости товаров в корзине"""

        total = 0
        for order_item in self.items.all():
            total += order_item.total_price()
        return total

    def clear_cart(self):
        """Удаление всех товаров из корзины"""

        self.items.all().delete()


class CartItem(models.Model):
    """Модель для товаров в корзине"""
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def total_price(self):
        return self.product.price * self.quantity

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"


class Order(models.Model):
    """Модель для заказа"""

    class Meta:
        ordering = ["-created_at", "updated_at"]
        verbose_name_plural = 'orders'

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    name = models.CharField(max_length=100, null=True)
    email = models.EmailField(null=True)
    phone = models.BigIntegerField(null=True)
    status = models.CharField(max_length=20,
                              choices=[
                                  ('pending', 'Ожидается'),
                                  ('processing', 'В обработке'),
                                  ('completed', 'Завершен'),
                                  ('canceled', 'Отменен'),
                              ],
                              default='pending')
    delivery_address = models.TextField(null=True, blank=True)
    payment_method = models.CharField(max_length=100, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class OrderItem(models.Model):
    """Модель для товара в заказе"""

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="order_items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def total_price(self):
        return self.product.price * self.quantity


class Review(models.Model):
    """Модель пользовательского отзыва на товар"""

    class Meta:
        ordering = ["-created_at", ]
        verbose_name_plural = 'reviews'

    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='review')
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    review_text = models.TextField(max_length=255, null=False, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review for {self.product.name} by {self.user.username}"
