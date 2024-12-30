from django.http import HttpRequest, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.views.generic import DetailView, ListView
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from .models import Product, Cart, CartItem, Category


class ProductDetailsView(DetailView):
    """Представление для отображения деталей товара"""

    template_name = 'shopapp/product_detail.html'
    queryset = Product.objects.select_related('category').prefetch_related('review')

    # context_object_name = 'product'
    def get_context_data(self, **kwargs):
        context = super(ProductDetailsView, self).get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context['cart'] = self.request.user.cart
        return context


class ProductsByCategoryListView(ListView):
    """Представление для отображения списка товаров в выбранной категории"""

    model = Product
    template_name = 'shopapp/products_list.html'
    # queryset = Product.objects.filter(category=category_id).select_related('category').prefetch_related('review')
    context_object_name = 'products'

    def get_queryset(self):
        queryset = super().get_queryset()

        category_id = dict(self.request.GET).get('category')[0]

        if category_id:
            queryset = queryset.filter(category=category_id)
        queryset.select_related('category')
        return queryset


class ProductsListView(ListView):
    """Представление для отображения списка товаров"""

    template_name = 'shopapp/products_list.html'
    queryset = Product.objects.select_related('category').order_by('category')
    context_object_name = 'products'


class CategoriesListView(ListView):
    """Представление для отображения списка категорий"""

    template_name = 'shopapp/categories_list.html'
    queryset = Category.objects.all()
    context_object_name = 'categories'


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
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@login_required
def reduce_items_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart, _ = Cart.objects.get_or_create(user=request.user)

    # Проверяем, есть ли товар уже в корзине
    cart_item, _ = CartItem.objects.get_or_create(cart=cart, product=product)
    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    else:
        cart_item.delete()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@login_required
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    cart_item.delete()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
