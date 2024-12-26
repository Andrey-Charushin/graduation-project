from django.db import models
from django.contrib.auth.models import User


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
        """Проверка наличия товара в наличии"""
        return self.stock > 0


class Order(models.Model):
    """Модель для заказа"""

    class Meta:
        ordering = ["-created_at", "updated_at"]
        verbose_name_plural = 'orders'

    user = models.ForeignKey(User, on_delete=models.PROTECT)
    products = models.ManyToManyField(Product, related_name='orders')
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20,
                              choices=[('pending', 'Pending'), ('shipped', 'Shipped'), ('delivered', 'Delivered')],
                              default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Review(models.Model):
    class Meta:
        ordering = ["-created_at",]
        verbose_name_plural = 'reviews'

    user = models.ForeignKey('auth.User', on_delete=models.PROTECT)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='review')
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    review_text = models.TextField(max_length=255, null=False, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review for {self.product.name} by {self.user.username}"