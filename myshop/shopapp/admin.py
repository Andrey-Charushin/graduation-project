from django.contrib import admin
from .models import Product, Category, Order, Review


# Register your models here.
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = "pk", "name", "description", "price", "stock", "category", "created_at", "updated_at"
    list_display_links = "pk", "name"
    ordering = "name", "price"
    search_fields = "name", "description"


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = "pk", "name", "description"
    list_display_links = "pk", "name"
    ordering = "pk", "name",
    search_fields = "name", "description"


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = "pk", "user_id", "total_price", "status", "created_at", "updated_at",
    list_display_links = "pk",

    def get_queryset(self, request):
        return Order.objects.select_related("user").prefetch_related("products")

    def user_verbose(self, obj: Order) -> str:
        return obj.user.first_name or obj.user.username

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = "pk", "product", "user", "rating"
    list_display_links = "pk",
