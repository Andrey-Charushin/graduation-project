from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from .views import (
    ProductDetailsView,
    ProductsListView,)

app_name = 'shopapp'

urlpatterns = [
    path('product/<int:pk>/', ProductDetailsView.as_view(), name='product_detail'),
    path('products/', ProductsListView.as_view(), name='products_list'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
