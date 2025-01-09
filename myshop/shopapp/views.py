import logging
from decimal import Decimal
from django.http import HttpRequest, HttpResponseRedirect, HttpResponse
from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views.generic import DetailView, ListView, CreateView, UpdateView
from django.views import View
from django.db import transaction
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django_filters.views import FilterView
from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend

from .models import Product, Cart, CartItem, Category, Order, OrderItem
from .forms import ReviewForm
from .serializers import ProductSerializer
from .filters import ProductFilter

log = logging.getLogger(__name__)


class AboutView(View):
    """Представление для отображения информации о магазине"""

    def get(self, request: HttpRequest) -> HttpResponse:
        log.info('Render about view')
        return render(request, 'shopapp/about.html')


class ContactsView(View):
    """Представление для отображения контактных данных"""

    def get(self, request: HttpRequest) -> HttpResponse:
        log.info('Render contacts view')
        return render(request, 'shopapp/contacts.html')


class ProductViewSet(ModelViewSet):
    """Представления товара для API"""
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filterset_fields = [
        "name",
        "description",
        "price"
    ]
    filter_backends = [
        SearchFilter,
        DjangoFilterBackend,
        OrderingFilter
    ]
    search_fields = ["name", "category", "description"]
    ordering_fields = [
        "pk",
        "name",
        "price",
    ]


class ProductsListView(FilterView):
    """Представление для отображения списка товаров"""

    model = Product
    template_name = 'shopapp/products_list.html'
    # queryset = Product.objects.select_related('category').order_by('category')
    context_object_name = 'products'
    filterset_class = ProductFilter

    def get_queryset(self):
        query = self.request.GET.get('query')  # Получаем поисковый запрос
        if query:
            return Product.objects.filter(name__icontains=query).select_related(
                'category').order_by('category')

        return Product.objects.select_related('category').order_by('category')


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


class ProductCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """Представление для создания товара"""

    model = Product
    fields = "name", "price", "description", "stock", "image", "category"
    success_url = reverse_lazy("shopapp:products_list")

    def test_func(self):
        # Ограничение для работников магазина
        return self.request.user.is_staff


class ProductUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Представление для редактирования товара"""

    model = Product
    fields = "name", "price", "description", "stock", "image", "category"
    template_name_suffix = "_update_form"

    def test_func(self):
        # Ограничение для работников магазина
        return self.request.user.is_staff

    def get_success_url(self):
        return reverse(
            "shopapp:product_detail",
            kwargs={"pk": self.object.pk},
        )


class CategoriesListView(ListView):
    """Представление для отображения списка категорий"""

    template_name = 'shopapp/categories_list.html'
    queryset = Category.objects.all()
    context_object_name = 'categories'


@login_required
def cart_detail(request):
    """Представление для пользовательской корзины товаров"""

    cart = get_object_or_404(Cart, user=request.user)
    context = {
        "cart": cart,

    }
    return render(request, "shopapp/cart_detail.html", context=context)


@login_required
def add_to_cart(request, product_id):
    """Представление для добавления единицы товара в корзину авторизованного пользователя"""

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
    """Удаление единицы товара из корзины"""

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
    """Удаление товара из корзины не зависимо от количества"""

    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    cart_item.delete()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@login_required
def clear_cart(request):
    """Удаление всех товаров из корзины"""

    cart = request.user.cart
    cart.clear_cart()

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@login_required
@transaction.atomic
def order_view(request):
    """Представление для оформления заказа"""

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

        # Добавление товарова из корзины к заказу
        for item in items:
            if item.quantity > item.product.stock:
                transaction.set_rollback(True)
                messages.error(request,
                               f"{item.product.name} отсутствует на складе в количестве {item.quantity} шт. "
                               f"Доступно для заказа {item.product.stock} шт")
                return redirect("shopapp:cart_detail")

            OrderItem.objects.create(order=order, product=item.product, quantity=item.quantity)
            item.product.stock -= item.quantity
            item.product.save()
            item.delete()

        order.save()

        messages.success(request, "Ваш заказ успешно оформлен!")
        return redirect("shopapp:cart_detail")

    return render(request, "shopapp/create_order.html")


class OrderListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """Представление для отображения списка заказов"""

    model = Order
    template_name = 'shopapp/orders_list.html'
    context_object_name = 'orders'

    def test_func(self):
        # Ограничение для работников магазина
        return self.request.user.is_staff


class OrderUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Представление для изменения статуса заказа"""
    model = Order
    fields = ['status']
    template_name = 'shopapp/order_update.html'
    success_url = reverse_lazy('shopapp:orders_list')

    def test_func(self):
        # Ограничение для работников магазина
        return self.request.user.is_staff


def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'shopapp/order_detail.html', {'order': order})


@login_required
def add_review(request, product_id):
    """Представление для создания отзыва на товар"""

    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.user = request.user
            review.save()
            return redirect('shopapp:product_detail', pk=product.id)
    else:
        form = ReviewForm()
    return render(request, 'shopapp/add_review.html', {'form': form, 'product': product})
