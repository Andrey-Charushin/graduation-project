from django.shortcuts import render, get_object_or_404
from django.views.generic import DetailView, ListView

from .models import Product


class ProductDetailsView(DetailView):
    """Представление для отображения деталей товара"""

    template_name = 'shopapp/product_detail.html'
    queryset = Product.objects.all()
    context_object_name = 'product'


class ProductsListView(ListView):
    template_name = 'shopapp/products_list.html'
    queryset = Product.objects.all()
    context_object_name = 'products'
