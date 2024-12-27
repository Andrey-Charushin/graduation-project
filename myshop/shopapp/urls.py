from django.urls import path
from django.conf import settings
from django.conf.urls.static import static


from .views import (
    ProductDetailsView,
    ProductsListView,
    cart_detail,
    add_to_cart,
    remove_from_cart,
)

app_name = 'shopapp'

urlpatterns = [
    path('product/<int:pk>/', ProductDetailsView.as_view(), name='product_detail'),
    path('products/', ProductsListView.as_view(), name='products_list'),
    path("cart/", cart_detail, name="cart_detail"),
    path("cart/add/<int:product_id>/", add_to_cart, name="add_to_cart"),
    path("cart/remove/<int:item_id>/", remove_from_cart, name="remove_from_cart"),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
