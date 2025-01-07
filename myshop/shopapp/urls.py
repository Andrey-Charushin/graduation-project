from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from rest_framework.routers import DefaultRouter


from .views import (
    AboutView,
    ContactsView,
    CategoriesListView,
    ProductViewSet,
    ProductDetailsView,
    ProductsListView,
    ProductCreateView,
    ProductUpdateView,
    cart_detail,
    add_to_cart,
    reduce_items_cart,
    remove_from_cart,
    order_view,
    add_review,
    clear_cart,
    OrderUpdateView,
    OrderListView,
    order_detail
)

app_name = 'shopapp'

routers = DefaultRouter()
routers.register("products", ProductViewSet)

urlpatterns = [
    path('', CategoriesListView.as_view(), name='categories'),
    path('about/', AboutView.as_view(), name='about'),
    path('contact/', ContactsView.as_view(), name='contact'),
    path("api/", include(routers.urls)),

    path('products/', ProductsListView.as_view(), name='products_list'),
    path('products/create', ProductCreateView.as_view(), name='product_create'),
    path('product/<int:pk>/', ProductDetailsView.as_view(), name='product_detail'),
    path('product/<int:pk>/update', ProductUpdateView.as_view(), name='product_update'),
    path('product/<int:product_id>/add_review/', add_review, name='add_review'),

    path("cart/", cart_detail, name="cart_detail"),
    path("cart/add/<int:product_id>/", add_to_cart, name="add_to_cart"),
    path("cart/reduce/<int:product_id>/", reduce_items_cart, name="reduce_items_cart"),
    path("cart/remove/<int:item_id>/", remove_from_cart, name="remove_from_cart"),
    path("cart/clear/", clear_cart, name="clear_cart"),

    path("order/", order_view, name="create_order"),
    path('orders/', OrderListView.as_view(), name='orders_list'),
    path('orders/<int:order_id>/', order_detail, name='order_detail'),
    path('orders/<int:pk>/update/', OrderUpdateView.as_view(), name='order_update'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
