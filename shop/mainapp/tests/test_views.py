from decimal import Decimal
from unittest import mock

from PIL import Image
from django.test import TestCase, RequestFactory, Client
from django.contrib.auth import get_user_model, authenticate, login
from django.core.files.uploadedfile import SimpleUploadedFile

from ..models import Category, Refrigerator, CartProduct, Cart, Customer
from ..utils import recalc_cart
from ..views import AddToCartView, BaseView, DeleteFromCartView, ChangeQtyView, RegistrationView

User = get_user_model()


class ShopTestCases(TestCase):

    def setUp(self) -> None:
        pass
        user = User.objects.create()
        user.username = 'Bobik'
        user.email = 'shop1234shop@gmail.com'
        user.first_name = 'Bob'
        user.last_name = 'smith'
        user.save()
        user.set_password('1234')
        user.save()
        self.user = authenticate(username=user.username, password='1234')
        self.customer = Customer.objects.create(
            user=self.user,
            phone='+375(44)1112233',
            address='TestAddress',
        )
        self.category = Category.objects.create(name='Холодильники', slug='refrigerators')
        image = SimpleUploadedFile(
            name='test_image.jpg',
            content=open('/home/yuliya/ISP/lab3-4/shop/media/r_bosh_seria_4.jpeg', 'rb').read(),
            content_type='image/jpeg'
        )
        self.refrigerator = Refrigerator.objects.create(
            category=self.category,
            title="Test Refrigerator",
            slug="test-slug",
            image=image,
            price=Decimal('1000.00'),
            overall_volume="500 л",
            useful_volume="450 л",
            control="механическое",
            noise_level="45 дБ",
            number_of_shelves="5",
            number_of_freezer_shelves="2"
        )
        self.cart = Cart.objects.create(owner=self.customer)
        self.cart_product = CartProduct.objects.create(
            user=self.customer,
            cart=self.cart,
            content_object=self.refrigerator
        )

    def test_registration(self):
        self.client.login(username=self.user.username, password='1234')
        self.assertIn(self.customer, Customer.objects.all())

        self.cart.products.add(self.cart_product)
        response = self.client.get('/add-to-cart/refrigerator/test-slug/', follow=True)
        message = list(response.context.get('messages'))[0]
        self.assertNotEqual(message.tags, "error")

    def test_add_to_cart_auth(self):
        self.client.login(username=self.user.username, password='1234')
        self.cart.products.add(self.cart_product)
        recalc_cart(self.cart)
        self.assertIn(self.cart_product, self.cart.products.all())
        self.assertEqual(self.cart.products.count(), 1)
        self.assertEqual(self.cart.final_price, Decimal('1000.00'))

        # use follow=True to follow redirect
        response = self.client.get('/add-to-cart/refrigerator/test-slug/', follow=True)

        # don't really need to check status code because assertRedirects will check it
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, '/cart/')

        # get message from context and check that expected text is there
        message = list(response.context.get('messages'))[0]
        self.assertEqual(message.tags, "info")
        self.assertTrue("Товар успешно добавлен" in message.message)

    def test_add_to_cart_not_auth(self):
        self.cart.products.add(self.cart_product)
        recalc_cart(self.cart)
        self.assertIn(self.cart_product, self.cart.products.all())
        self.assertEqual(self.cart.products.count(), 1)
        self.assertEqual(self.cart.final_price, Decimal('1000.00'))

        # use follow=True to follow redirect
        response = self.client.get('/add-to-cart/refrigerator/test-slug/', follow=True)

        # don't really need to check status code because assertRedirects will check it
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, '/')

        # get message from context and check that expected text is there
        message = list(response.context.get('messages'))[0]
        self.assertEqual(message.tags, "error")
        self.assertTrue("Для добавления товаров в корзину пройдите авторизацию/регистрацию" in message.message)

    def test_delete_from_cart(self):
        self.client.login(username=self.user.username, password='1234')
        self.cart.products.remove(self.cart_product)
        recalc_cart(self.cart)
        self.assertNotIn(self.cart_product, self.cart.products.all())
        self.assertEqual(self.cart.products.count(), 0)

    def test_change_in_cart(self):
        self.client.login(username=self.user.username, password='1234')
        self.cart.products.add(self.cart_product)
        self.cart_product.qty += 1
        self.cart_product.save()
        recalc_cart(self.cart)
        self.assertIn(self.cart_product, self.cart.products.all())
        self.assertEqual(self.cart.products.count(), 1)
        self.assertEqual(self.cart.final_price, Decimal('2000.00'))

    # def test_response_from_add_to_cart_view(self):
    #     factory = RequestFactory()
    #     request = factory.get('')
    #     request.user = self.user
    #     response = AddToCartView.as_view()(request, ct_model="refrigerator", slug="test-slug")
    #     self.assertEqual(response.status_code, 302)
    #     self.assertEqual(response.url, '/cart/')

    # def test_response_from_delete_from_cart_view(self):
    #     factory = RequestFactory()
    #     request = factory.get('')
    #     request.user = self.user
    #     response = DeleteFromCartView.as_view()(request, ct_model="refrigerator", slug="test-slug")
    #     self.assertEqual(response.status_code, 302)
    #     self.assertEqual(response.url, '/cart/')

    def test_mock_homepage(self):
        mack_data = mock.Mock(status_code=444)
        with mock.patch('mainapp.views.BaseView.get', return_value=mack_data) as mock_data_:
            factory = RequestFactory()
            request = factory.get('')
            request.user = self.user
            response = BaseView.as_view()(request)
            self.assertEqual(response.status_code, 444)
            print(mock_data_.called)
