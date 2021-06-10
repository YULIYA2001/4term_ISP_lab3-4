import sys
from PIL import Image
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from django.core.files.uploadedfile import InMemoryUploadedFile

from io import BytesIO


# использование юзера из настроек (в начале создания проекта, был создан суперюзер)
# settings.AUTH_USER_MODEL
User = get_user_model()


def get_models_for_count(*model_names):
    return [models.Count(model_name) for model_name in model_names]


class LatestProductsManager:

    @staticmethod
    def get_products_for_main_page(*args, **kwargs):
        # приоритет выдачи списка из 5 товаров
        with_respect_to = kwargs.get('with_respect_to')
        # список всех объектов моделей, для которых хотим вывести товары на главной странице
        products = []
        ct_models = ContentType.objects.filter(model__in=args)
        for ct_model in ct_models:
            model_products = ct_model.model_class()._base_manager.all().order_by('-id')[:5]
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
    objects = LatestProductsManager()


class CategoryManager(models.Manager):
    CATEGORY_NAME_COUNT_NAME = {
        'Холодильники': 'refrigerator__count',
        'Стиральные машины': 'washer__count',
        'Посудомоечные машины': 'dishwasher__count'
    }

    def get_queryset(self):
        return super().get_queryset()

    def get_categories_for_up_sidebar(self):
        models = get_models_for_count('dishwasher', 'refrigerator', 'washer')
        qs = list(self.get_queryset().annotate(*models))
        data = [
            dict(name=c.name, url=c.get_absolute_url(), count=getattr(c, self.CATEGORY_NAME_COUNT_NAME[c.name]))
            for c in qs
        ]
        return data


class Category(models.Model):
    name = models.CharField(max_length=255, verbose_name='Имя категории')
    # url .../categories/slug, только адекватное имя вместо slug
    slug = models.SlugField(unique=True)
    objects = CategoryManager()

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('category_detail', kwargs={'slug': self.slug})

    def get_fields_for_filter_in_template(self):
        return ProductFeatures.objects.filter(
            category=self,
            use_in_filter=True
        ).prefeatch_related('category').value('feature_key', 'feature_measure', 'feature_name', 'filter_type')


class Product(models.Model):
    # масштабирование всех картинок до 700х400
    THUMBNAIL_SIZE = (300, 400)

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

    def get_model_name(self):
        return self.__class__.__name__.lower()

    def save(self, *args, **kwargs):
        # уменьшение картинки до нужных размеров
        background = Image.new('RGB', self.THUMBNAIL_SIZE, "white")
        source_image = Image.open(self.image).convert("RGB")
        source_image.thumbnail(self.THUMBNAIL_SIZE)
        (w, h) = source_image.size
        background.paste(source_image, ((self.THUMBNAIL_SIZE[0] - w) // 2, (self.THUMBNAIL_SIZE[1] - h) // 2))
        filestream = BytesIO()
        background.save(filestream, 'JPEG', quality=90)
        filestream.seek(0)
        name = '{}.{}'.format(*self.image.name.split('.'))
        self.image = InMemoryUploadedFile(
            filestream, 'ImageField', name, 'jpeg/image', sys.getsizeof(filestream), None
        )
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('product_detail', kwargs={'slug': self.slug})


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
        return "/products/refrigerator/" + self.slug


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
        return "/products/washer/" + self.slug


class Dishwasher(Product):
    max_load = models.CharField(max_length=255, verbose_name='Максимальная загрузка (комплекты посуды)')
    drying = models.BooleanField(default=True, verbose_name='Наличие сушки')
    drying_type = models.CharField(max_length=255, null=True, blank=True, verbose_name='Тип сушки')
    number_of_programs = models.CharField(max_length=255, verbose_name='Количество программ')
    noise_level = models.CharField(max_length=255, verbose_name='Уровень шума')
    shortest_program = models.CharField(max_length=255, verbose_name='Время самой короткой программы')
    water_consumption_per_cycle = models.CharField(max_length=255, verbose_name='Расход воды за цикл')
    control = models.CharField(max_length=255, verbose_name='Тип управления')
    child_lock = models.BooleanField(default=True, verbose_name='Блокировка от детей')

    def __str__(self):
        return "{} : {}".format(self.category.name, self.title)

    def get_absolute_url(self):
        return "/products/dishwasher/" + self.slug


class CartProduct(models.Model):
    user = models.ForeignKey('Customer', verbose_name='Покупатель', on_delete=models.CASCADE)
    cart = models.ForeignKey('Cart', verbose_name='Корзина', on_delete=models.CASCADE, related_name='related_products')

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    #product = models.ForeignKey(Product, verbose_name='Товар', on_delete=models.CASCADE)
    qty = models.PositiveIntegerField(default=1)
    final_price = models.DecimalField(max_digits=9, decimal_places=2, verbose_name='Общая стоимость')

    def __str__(self):
        return "Продукт: {} (для корзины)".format(self.content_object.title)

    def save(self, *args, **kwargs):
        self.final_price = self.qty * self.content_object.price
        super().save(*args, **kwargs)


class Cart(models.Model):
    owner = models.ForeignKey('Customer', null=True, verbose_name='Владелец', on_delete=models.CASCADE)
    products = models.ManyToManyField(CartProduct, blank=True, related_name='related_cart')
    # для корректного отображения одинаковых товаров в корзине (показывать только уникальные)
    total_products = models.PositiveIntegerField(default=0)
    final_price = models.DecimalField(max_digits=9, default=0, decimal_places=2, verbose_name='Общая стоимость')
    in_order = models.BooleanField(default=False)
    for_anonymous_user = models.BooleanField(default=False)

    def __str__(self):
        return str(self.id)


class Customer(models.Model):
    user = models.ForeignKey(User, verbose_name='Пользователь', on_delete=models.CASCADE)
    phone = models.CharField(max_length=20, verbose_name='Номер телефона', null=True, blank=True)
    address = models.CharField(max_length=255, verbose_name='Адрес', null=True, blank=True)
    orders = models.ManyToManyField('Order', verbose_name='Заказы покупателя', related_name='related_customer')

    def __str__(self):
        return 'Покупатель {} {}'.format(self.user.first_name, self.user.last_name)


class Order(models.Model):
    STATUS_NEW = 'new'
    STATUS_IN_PROGRESS = 'in_progress'
    STATUS_READY = 'ready'
    STATUS_COMPLETED = 'completed'

    BUYING_TYPE_SELF = 'self'
    BUYING_TYPE_DELIVERY = 'delivery'

    STATUS_CHOICES = (
        (STATUS_NEW, 'Новый заказ'),
        (STATUS_IN_PROGRESS, 'Заказ в обработке'),
        (STATUS_READY, 'Заказ готов'),
        (STATUS_COMPLETED, 'Заказ завершен')
    )

    BUYING_TYPE_CHOICES = (
        (BUYING_TYPE_SELF, 'Самовывоз'),
        (BUYING_TYPE_DELIVERY, 'Доставка')
    )

    customer = models.ForeignKey(Customer, verbose_name='Покупатель', related_name='related_orders', on_delete=models.CASCADE)
    first_name = models.CharField(max_length=255, verbose_name='Имя')
    last_name = models.CharField(max_length=255, verbose_name='Фамилия')
    phone = models.CharField(max_length=255, verbose_name='Телефон')
    cart = models.ForeignKey(Cart, verbose_name='Корзина', on_delete=models.CASCADE, null=True, blank=True)
    address = models.CharField(max_length=1024, verbose_name='Адрес', null=True, blank=True)
    status = models.CharField(
        max_length=100, verbose_name='Статус заказа', choices=STATUS_CHOICES, default=STATUS_NEW
    )
    buying_type = models.CharField(
        max_length=100, verbose_name='Тип заказа', choices=BUYING_TYPE_CHOICES, default=BUYING_TYPE_SELF
    )
    comment = models.TextField(verbose_name='Комментарий к заказу', null=True, blank=True)
    created_at = models.DateTimeField(auto_now=True, verbose_name='Дата создания заказа')
    order_date = models.DateField(verbose_name='Дата получения заказа', default=timezone.now)

    def __str__(self):
        return str(self.id)


# class ProductFeatures(models.Model):
#
#     RADIO = 'radio'
#     CHECKBOX = 'checkbox'
#
#     FILTER_TYPE_CHOICES = (
#         (RADIO, 'Радиокнопка'),
#         (CHECKBOX, 'Чекбокс')
#     )
#     feature_key = models.CharField(max_length=100, verbose_name='Наименование характеристики')
#     feature_name = models.CharField(max_length=255, verbose_name='Ключ характеристики')
#     category = models.ForeignKey(Category, verbose_name='Категория', on_delete=models.CASCADE)
#     postfix_for_value = models.CharField(
#         max_length=20,
#         null=True,
#         blank=True,
#         verbose_name='Постфикс для значения',
#         help_text=f'Например для характеристики "Общий объем" можно добавить постфикс "л" (45 л)'
#     )
#     use_in_filter = models.BooleanField(
#         default=False,
#         verbose_name='Использовать фильтрации товаров в шаблоне'
#     )
#     filter_type = models.CharField(
#         max_length=20,
#         verbose_name='Тип фильтра',
#         default=CHECKBOX,
#         choices=FILTER_TYPE_CHOICES
#     )
#     filter_measure = models.CharField(
#         max_length=50,
#         verbose_name='Единица измерения для фильтра',
#         help_text='Единица измерения для конкретного фильтра. Например "Расход энергии (кВт·ч)".'
#                   ' Единица измерения - информация в скобках.'
#     )
#
#     def __str__(self):
#         return f'Категория - "{self.category.name}" | Характеристика - "{self.feature_name}"'
#
#
# class ProductFeatureValidators(models.Model):
#
#     category = models.ForeignKey(Category, verbose_name='Категория', on_delete=models.CASCADE)
#     feature = models.ForeignKey(
#         ProductFeatures, verbose_name='Характеристика', null=True, blank=True, on_delete=models.CASCADE
#     )
#     feature_value = models.CharField(
#         max_length=255, unique=True, null=True, blank=True, verbose_name='Значение характеристики'
#     )
#
#     def __str__(self):
#         if not self.feature:
#             return f'Валидатор категории "{self.category.name}" - характеристика не выбрана'
#         return f'Валидатор категории "{self.category.name}" | ' \
#             f'Характеристика "{self.feature.feature_name}" | ' \
#             f'Значение "{self.feature_value}"'

