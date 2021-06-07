# import sys
# from PIL import Image

from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.urls import reverse

# from django.core.files.uploadedfile import InMemoryUploadedFile

# from io import BytesIO

# использование юзера из настроек (в начале создания проекта, был создан суперюзер)
# settings.AUTH_USER_MODEL
User = get_user_model()


def get_product_url(obj, viewname):
    ct_model = obj.__class__._meta.model_name
    return reverse(viewname, kwargs={'ct-model': ct_model, 'slug': obj.slug})


class MinResolutionErrorException(Exception):
    pass


class MaxResolutionErrorException(Exception):
    pass


class LatestProductsManager:

    @staticmethod
    def get_products_for_main_page(*args, **kwargs):
        # приоритет выдачи списка из 5 товаров
        with_respect_to = kwargs.get('with_respect_to')
        # список всех объектов моделей, для которых хотим вывести товары на главной странице
        products = []
        ct_models = ContentType.objects.filter(model__in=args)
        for ct_model in ct_models:
            model_products = ct_model. model_class()._base_manager.all().order_by('-id')[:5]
            products.extend(model_products)
        if with_respect_to:
            ct_model = ContentType.objects.filter(model=with_respect_to)
            if ct_model.exists():
                if with_respect_to in args:
                    return sorted(
                        products, key=lambda x: x.__class__._meta.model_name.startswith(with_respect_to), reverse=True
                    )
        return products


class LatestProducts:

    objects = LatestProductsManager


# --------------
# 1 Category
# 2 Product
# 3 CartProduct
# 4 Cart
# 5 Order
# ---------------
# 6 Customer
# 7 Specifications (Характеристики)

class Category(models.Model):
    name = models.CharField(max_length=255, verbose_name='Имя категории')
    # url .../categories/slug, только адекватное имя вместо slug
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    MIN_RESOLUTION = (50, 50)
    MAX_RESOLUTION = (1000, 1000)
    # 3 Мб = 3145728 б
    MAX_IMAGE_SIZE = 3145728

    # данная модель - абстрактная (нельзя создать миграцию)
    class Meta:
        abstract = True

    # on_delete=models.CASCADE при удалении удалить все связи с этим объектом
    category = models.ForeignKey(Category, verbose_name='Категория', on_delete=models.CASCADE)
    title = models.CharField(max_length=255, verbose_name='Наименование')
    slug = models.SlugField(unique=True)
    image = models.ImageField(verbose_name='Изображение')
    description = models.TextField(verbose_name='Описание', null=True)
    price = models.DecimalField(max_digits=9, decimal_places=2, verbose_name='Цена')

    def __str__(self):
        return self.title

    # def save(self, *args, **kwargs):
    #     image = self.image
    #     img = Image.open(image)
    #     min_height, min_width = self.MIN_RESOLUTION
    #     max_height, max_width = self.MAX_RESOLUTION
    #     if img.height < min_height or img.width < min_width:
    #         raise MinResolutionErrorException('Разрешение загруженного изображения меньше минимального!')
    #     if img.height > max_height or img.width > max_width:
    #         raise MaxResolutionErrorException('Разрешение загруженного изображения больше максимального!')
    #     # # принудительная обрезка файла
    #     # image = self.image
    #     # img = Image.open(image)
    #     # new_image = Image.convert('RGB')
    #     # resized_new_image = new_image.resize((200, 200), Image.ANTIALIAS)
    #     # filestream = BytesIO()
    #     # resized_new_image.save(filestream, 'JPEG', quality=90)
    #     # filestream.seek(0)
    #     # name = '{}.{}'.format(*self.image.name.split('.'))
    #     # self.image = InMemoryUploadedFile(
    #     #     filestream, 'ImageField', name, 'jpeg/image', sys.getsizeof(filestream), None
    #     # )
    #     super().save(*args, **kwargs)

# Холодильник
#
# общий объем
# полезный объем
# управление
# уровень шума
# количество полок
# количество отделений морозильной камеры


class Refrigerator(Product):
    overall_volume = models.CharField(max_length=255, verbose_name='Общий объем')
    useful_volume = models.CharField(max_length=255, verbose_name='Полезный объем')
    control = models.CharField(max_length=255, verbose_name='Тип управления')
    noise_level = models.CharField(max_length=255, verbose_name='Уровень шума')
    number_of_shelves = models.CharField(max_length=255, verbose_name='Количество полок')
    number_of_freezer_shelves = models.CharField(max_length=255, verbose_name='Количество полок морозильной камеры')

    def __str__(self):
        return "{} : {}".format(self.category.name, self.title)

    def get_absolute_url(self):
        return get_product_url(self, 'product_detail')


# Стиральная машина
#
# Максимальная загрузка
# Максимальная скорость отжима
# Количество программ
# Самая короткая программа
# Расход электроэнергии за цикл
# Расход воды за цикл


class Washer(Product):
    max_loading = models.CharField(max_length=255, verbose_name='Максимальный объем загрузки')
    max_spin_speed = models.CharField(max_length=255, verbose_name='Максимальная скорость отжима')
    number_of_programs = models.CharField(max_length=255, verbose_name='Количество программ стирки')
    shortest_program = models.CharField(max_length=255, verbose_name='Время самой короткой программы')
    electricity_consumption_per_cycle = models.CharField(max_length=255, verbose_name='Расход электроэнергии за цикл')
    water_consumption_per_cycle = models.CharField(max_length=255, verbose_name='Расход воды за цикл')

    def __str__(self):
        return "{} : {}".format(self.category.name, self.title)

    def get_absolute_url(self):
        return get_product_url(self, 'product_detail')


# Посудомоечная машина
#
# Максимальная загрузка (комплекты посуды)
# Сушка
# Количество программ
# Уровень шума
# Самая короткая программа
# Расход воды за цикл
# Управление
# Блокировка от детей


class Dishwasher(Product):
    max_load = models.CharField(max_length=255, verbose_name='Максимальная загрузка (комплекты посуды)')
    drying = models.BooleanField(default=True)
    drying_type = models.CharField(max_length=255, verbose_name='Тип сушки')
    number_of_programs = models.CharField(max_length=255, verbose_name='Количество программ')
    noise_level = models.CharField(max_length=255, verbose_name='Уровень шума')
    shortest_program = models.CharField(max_length=255, verbose_name='Время самой короткой программы')
    water_consumption_per_cycle = models.CharField(max_length=255, verbose_name='Расход воды за цикл')
    control = models.CharField(max_length=255, verbose_name='Тип управления')
    child_lock = models.BooleanField(default=True)

    def __str__(self):
        return "{} : {}".format(self.category.name, self.title)

    def get_absolute_url(self):
        return get_product_url(self, 'product_detail')


class CartProduct(models.Model):
    user = models.ForeignKey('Customer', verbose_name='Покупатель', on_delete=models.CASCADE)
    cart = models.ForeignKey('Cart', verbose_name='Корзина', on_delete=models.CASCADE, related_name='related_products')
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    qty = models.PositiveIntegerField(default=1)
    final_price = models.DecimalField(max_digits=9, decimal_places=2, verbose_name='Общая стоимость')

    def __str__(self):
        return "Продукт: {} (для корзины)".format(self.content_object.title)


class Cart(models.Model):
    owner = models.ForeignKey('Customer', verbose_name='Владелец', on_delete=models.CASCADE)
    products = models.ManyToManyField(CartProduct, blank=True, related_name='related_cart')
    # для корректного отображения одинаковых товаров в корзине (показывать только уникальные)
    total_products = models.PositiveIntegerField(default=0)
    final_price = models.DecimalField(max_digits=9, decimal_places=2, verbose_name='Общая стоимость')
    in_order = models.BooleanField(default=False)
    for_anonymous_user = models.BooleanField(default=False)

    def __str__(self):
        return str(self.id)


class Customer(models.Model):
    user = models.ForeignKey(User, verbose_name='Пользователь', on_delete=models.CASCADE)
    phone = models.CharField(max_length=20, verbose_name='Номер телефона')
    address = models.CharField(max_length=255, verbose_name='Адрес')

    def __str__(self):
        return 'Покупатель {} {}'.format(self.user.first_name, self.user.last_name)