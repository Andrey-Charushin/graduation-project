from django.urls import path
from django.conf import settings
from django.conf.urls.static import static


from .views import (
    AboutView,
    CategoriesListView,
    ProductsByCategoryListView,
    ProductDetailsView,
    ProductsListView,
    cart_detail,
    add_to_cart,
    reduce_items_cart,
    remove_from_cart,
    order_view,
    add_review,
    clear_cart
)

app_name = 'shopapp'

urlpatterns = [
    path('', CategoriesListView.as_view(), name='categories'),
    path('about/', AboutView.as_view(), name='about'),
    path('products/', ProductsListView.as_view(), name='products_list'),
    path('products/<int:pk>', ProductsByCategoryListView.as_view(), name='category_products'),
    path('product/<int:pk>/', ProductDetailsView.as_view(), name='product_detail'),
    path('product/<int:product_id>/add_review/', add_review, name='add_review'),
    path("cart/", cart_detail, name="cart_detail"),
    path("cart/add/<int:product_id>/", add_to_cart, name="add_to_cart"),
    path("cart/reduce/<int:product_id>/", reduce_items_cart, name="reduce_items_cart"),
    path("cart/remove/<int:item_id>/", remove_from_cart, name="remove_from_cart"),
    path("cart/clear/", clear_cart, name="clear_cart"),
    path("order/", order_view, name="create_order"),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
