from django.shortcuts import render, get_object_or_404
from django.views.generic import DetailView, ListView

from .models import Product


class ProductDetailsView(DetailView):
    """Представление для отображения деталей товара"""

    template_name = 'shopapp/product_detail.html'
    queryset = Product.objects.select_related('category').prefetch_related('review')
    context_object_name = 'product'


class ProductsListView(ListView):
    """Представление для отображения списка товаров"""

    template_name = 'shopapp/products_list.html'
    queryset = Product.objects.select_related('category').prefetch_related('review')
    context_object_name = 'products'
