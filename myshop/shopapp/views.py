from django.http import HttpRequest, HttpResponseRedirect, HttpResponse
from django.shortcuts import render, get_object_or_404
from django.views.generic import DetailView, ListView
from django.views import View
from django.db import transaction
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from decimal import Decimal
from .models import Product, Cart, CartItem, Category, Order, OrderItem


class AboutView(View):
    """Представление для отображения информации о магазине"""

    def get(self, request: HttpRequest) -> HttpResponse:
        return render(request, 'shopapp/about.html')


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


@login_required
@transaction.atomic
def order_view(request):
    if request.method == "POST":
        cart = request.user.cart
        items = cart.items.select_related('product')
        total_price = Decimal(cart.get_total())
        name = request.POST.get("name")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        address = request.POST.get("address")
        city = request.POST.get("city")
        zip_code = request.POST.get("zip")
        payment_method = request.POST.get("payment_method")

        # Удаление товаров со склада

        # Создание объекта заказа
        order = Order.objects.create(
            user=request.user,
            total_price=total_price,
            name=name,
            email=email,
            phone=phone,
            delivery_address=f'{city}, {address}, {zip_code}',
            payment_method=payment_method,
        )
        for item in items:
            if item.quantity > item.product.stock:
                transaction.set_rollback(True)
                messages.error(request,
                               f"{item.product.name} отсутствует на складе в количестве {item.quantity} шт. "
                               f"Доступно для заказа {item.product.stock}")
                return redirect("shopapp:cart_detail")

            OrderItem.objects.create(order=order, product=item.product, quantity=item.quantity)
            item.product.stock -= item.quantity
            item.product.save()
            item.delete()

        order.save()

        messages.success(request, "Ваш заказ успешно оформлен!")
        return redirect("shopapp:cart_detail")

    return render(request, "shopapp/create_order.html")
