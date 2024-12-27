from django.shortcuts import render, get_object_or_404
from django.views.generic import DetailView, ListView
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required

from .models import Product, Cart, CartItem


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

@login_required
def cart_detail(request):
    cart = get_object_or_404(Cart, user=request.user)
    context = {
        "cart": cart,
    }
    return render(request, "shopapp/cart_detail.html", context=context)

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart, _ = Cart.objects.get_or_create(user=request.user)

    # Проверяем, есть ли товар уже в корзине
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    if not created:
        cart_item.quantity += 1
    cart_item.save()
    return redirect("shopapp:cart_detail")

@login_required
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    cart_item.delete()
    return redirect("shopapp:cart_detail")