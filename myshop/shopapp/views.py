from django.shortcuts import render, get_object_or_404
from .models import Product

def product_detail(request, product_id):
    """Представление для отображения деталей товара"""
    product = get_object_or_404(Product, id=product_id)
    context = {
        "product": product,
    }
    return render(request, 'shopapp/product_detail.html', context=context)