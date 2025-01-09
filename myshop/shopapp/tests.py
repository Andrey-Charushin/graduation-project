from decimal import Decimal

from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from django.conf import settings
from django.shortcuts import get_object_or_404

from string import ascii_letters
from random import choices, randint

from shopapp.models import Product, Category, Cart, CartItem, Order, OrderItem, Review


class AboutViewTestCase(TestCase):
    def test_about_view(self):
        response = self.client.get(reverse("shopapp:about"))
        self.assertContains(response, "О нас")


class ContactsViewTestCase(TestCase):
    def test_contacts_view(self):
        response = self.client.get(reverse("shopapp:contact"))
        self.assertContains(response, "Контакты")


class CategoriesListViewTestCase(TestCase):
    fixtures = [
        'categories-fixture.json',
    ]

    def test_categories(self):
        response = self.client.get(reverse("shopapp:categories"))
        self.assertQuerySetEqual(
            qs=Category.objects.all(),
            values=(p.pk for p in response.context["categories"]),
            transform=lambda p: p.pk,
        )
        self.assertTemplateUsed(response, 'shopapp/categories_list.html')

    def test_categories_list_view(self):
        response = self.client.get(reverse("shopapp:categories"))
        self.assertEqual(response.status_code, 200)


class ProductCreateViewTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.category = Category.objects.create(name='Test_category')
        cls.credentials = dict(username='AdminTest', password='qwerty')
        cls.user = User.objects.create_user(**cls.credentials, is_staff=True)

    @classmethod
    def tearDownClass(cls):
        cls.user.delete()

    def setUp(self):
        self.client.login(**self.credentials)

        self.product_name = "".join(choices(ascii_letters, k=10))
        Product.objects.filter(name=self.product_name).delete()

    def test_product_create(self):
        response = self.client.post(reverse("shopapp:product_create"),
                                    {
                                        "name": self.product_name,
                                        "price": "123",
                                        "description": "A good table",
                                        "stock": "20",
                                        "image": "",
                                        "category": self.category.id
                                    })
        self.assertRedirects(response, reverse("shopapp:products_list"))
        self.assertTrue(
            Product.objects.filter(name=self.product_name).exists()
        )

    def test_product_create_not_authenticated(self):
        self.client.logout()
        response = self.client.post(reverse("shopapp:product_create"),
                                    {
                                        "name": self.product_name,
                                        "price": "123",
                                        "description": "A good table",
                                        "stock": "20",
                                        "image": "",
                                        "category": self.category.id
                                    })
        self.assertEqual(response.status_code, 302)
        self.assertIn(str(settings.LOGIN_URL), response.url)


class ProductDetailsViewTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.product_name = "".join(choices(ascii_letters, k=10))
        cls.category = Category.objects.create(name='Test_category')
        cls.product = Product.objects.create(name=cls.product_name, price="123", category_id="1")

    @classmethod
    def tearDownClass(cls):
        cls.product.delete()

    def test_get_product(self):
        response = self.client.get(
            reverse("shopapp:product_detail", kwargs={"pk": self.product.pk})
        )
        self.assertEqual(response.status_code, 200)

    def test_get_product_and_check_content(self):
        response = self.client.get(
            reverse("shopapp:product_detail", kwargs={"pk": self.product.pk})
        )
        self.assertContains(response, self.product.name)


class ProductsListViewTestCase(TestCase):
    fixtures = [
        'products-fixture.json',
        'categories-fixture.json',
    ]

    def test_products(self):
        response = self.client.get(reverse("shopapp:products_list"))
        self.assertQuerySetEqual(
            qs=Product.objects.select_related('category').order_by('category').all(),
            values=(p.pk for p in response.context["products"]),
            transform=lambda p: p.pk,
        )
        self.assertTemplateUsed(response, 'shopapp/products_list.html')

    def test_products_list_view(self):
        response = self.client.get(reverse("shopapp:products_list"))
        self.assertEqual(response.status_code, 200)


class CartTestCase(TestCase):
    fixtures = [
        'products-fixture.json',
        'categories-fixture.json',
    ]

    @classmethod
    def setUpClass(cls):
        cls.credentials = dict(username='AdminTest2', password='qwerty')
        cls.user = User.objects.create_user(**cls.credentials)
        cls.cart, _ = Cart.objects.get_or_create(user=cls.user)
        for product in Product.objects.all():
            CartItem.objects.create(cart=cls.cart, product=product, quantity=randint(2, 8))

    @classmethod
    def tearDownClass(cls):
        cls.user.delete()

    def setUp(self):
        self.client.login(**self.credentials)

    def test_cart_detail(self):
        response = self.client.get(reverse("shopapp:cart_detail"))
        self.assertQuerySetEqual(
            qs=self.cart.items.all(),
            values=(i.pk for i in response.context["cart"].items.all()),
            transform=lambda i: i.pk,
        )
        self.assertTemplateUsed(response, 'shopapp/cart_detail.html')


class OrdersListTestCase(TestCase):
    fixtures = [
        'products-fixture.json',
        'categories-fixture.json',
        'orders-fixture.json',
    ]

    @classmethod
    def setUpClass(cls):
        cls.credentials = dict(username='AdminTest3', password='qwerty', is_staff=True)
        cls.user = User.objects.create_user(**cls.credentials)
        cls.order = Order.objects.create(user=cls.user)

    @classmethod
    def tearDownClass(cls):
        cls.user.delete()

    def setUp(self):
        self.client.login(**self.credentials)

    def test_order_list_view(self):
        response = self.client.get(reverse("shopapp:orders_list"))
        self.assertQuerySetEqual(
            qs=Order.objects.all(),
            values=(o.pk for o in response.context["orders"]),
            transform=lambda o: o.pk,
        )
        self.assertTemplateUsed(response, 'shopapp/orders_list.html')


class OrderDetailTestCase(TestCase):
    fixtures = [
        'products-fixture.json',
        'categories-fixture.json',
        'orders-fixture,json',
    ]

    @classmethod
    def setUpClass(cls):
        cls.credentials = dict(username='AdminTest2', password='qwerty', is_staff=True)
        cls.user = User.objects.create_user(**cls.credentials)
        cls.order = Order.objects.create(user=cls.user)

    @classmethod
    def tearDownClass(cls):
        cls.user.delete()

    def setUp(self):
        self.client.login(**self.credentials)

    def test_order_detail_view(self):
        response = self.client.get(reverse("shopapp:order_detail", kwargs={"order_id": self.order.id}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'shopapp/order_detail.html')


class OrderViewTestCase(TestCase):
    fixtures = [
        'products-fixture.json',
        'categories-fixture.json',
        'orders-fixture.json',
    ]

    @classmethod
    def setUpClass(cls):
        cls.credentials = dict(username='AdminTest2', password='qwerty', is_staff=True)
        cls.user = User.objects.create_user(**cls.credentials)
        cls.cart, _ = Cart.objects.get_or_create(user=cls.user)
        cls.category = Category.objects.create(name="Test")
        cls.product = Product.objects.create(name="Test_product1", price="123", stock="2", category=cls.category)
        CartItem.objects.create(cart=cls.cart, product=cls.product, quantity=2)
        cls.product = Product.objects.create(name="Test_product2", price="123", stock="4", category=cls.category)
        CartItem.objects.create(cart=cls.cart, product=cls.product, quantity=2)

    @classmethod
    def tearDownClass(cls):
        cls.user.delete()

    def setUp(self):
        self.client.login(**self.credentials)

    def tearDown(self):
        Order.objects.filter(user=self.user).delete()

    def test_order_create(self):
        response = self.client.post(reverse("shopapp:create_order"),
                                    {

                                        "name": "TestName",
                                        "email": "example@mail.ru",
                                        "phone": 88009991235,
                                        "address": "ul. Pushkina",
                                        "city": "Moscow",
                                        "zip_code": "124587",
                                        "payment_method": "cash"
                                    })

        self.assertRedirects(response, reverse("shopapp:cart_detail"))
        self.assertTrue(
            Order.objects.filter(user=self.user).exists()
        )

    def test_order_create_not_authenticated(self):
        self.client.logout()
        response = self.client.post(reverse("shopapp:create_order"),
                                    {
                                        "cart": self.cart,
                                        "items": self.cart.items.select_related('product'),
                                        "total_price": Decimal(self.cart.get_total()),
                                        "name": "TestName",
                                        "email": "example@mail.ru",
                                        "phone": "88009991235",
                                        "address": "ul. Pushkina",
                                        "city": "Moscow",
                                        "zip_code": "124587",
                                        "payment_method": "cash",
                                    })
        self.assertEqual(response.status_code, 302)
        self.assertIn(str(settings.LOGIN_URL), response.url)

    def test_order_create_no_products_in_stock(self):
        self.product = Product.objects.create(name="Test_product3", price="123", stock="2", category=self.category)
        CartItem.objects.create(cart=self.cart, product=self.product, quantity=4)
        response = self.client.post(reverse("shopapp:create_order"),
                                    {

                                        "name": "TestName",
                                        "email": "example@mail.ru",
                                        "phone": 88009991235,
                                        "address": "ul. Pushkina",
                                        "city": "Moscow",
                                        "zip_code": "124587",
                                        "payment_method": "cash"
                                    })

        self.assertRedirects(response, reverse("shopapp:cart_detail"))
        self.assertFalse(
            Order.objects.filter(user=self.user).exists()
        )
        self.assertTrue(
            CartItem.objects.filter(cart=self.cart).exists()
        )


class AddReviewTestCase(TestCase):
    fixtures = [
        'products-fixture.json',
        'categories-fixture.json',
        'orders-fixture.json',
    ]

    @classmethod
    def setUpClass(cls):
        cls.credentials = dict(username='AdminTest4', password='qwerty', is_staff=True)
        cls.user = User.objects.create_user(**cls.credentials)
        cls.category = Category.objects.create(name="Test2")
        cls.product = Product.objects.create(name="Test_product1", price="123", stock="2", category=cls.category)

    @classmethod
    def tearDownClass(cls):
        cls.user.delete()

    def setUp(self):
        self.client.login(**self.credentials)

    def test_add_review(self):
        response = self.client.post(reverse("shopapp:add_review", kwargs={"product_id": self.product.id}),
                                    {
                                        'review_text': 'some text for test',
                                        'rating': 3
                                    })

        self.assertRedirects(response, reverse('shopapp:product_detail', kwargs={"pk": self.product.id}))
        self.assertTrue(
            Review.objects.filter(user=self.user).exists()
        )
