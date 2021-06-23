from django.test import TestCase
from ..models import Category


class CategoryModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        Category.objects.create(name='Холодильники', slug='refrigerators')

    def test_name_label(self):
        category = Category.objects.get(id=1)
        field_label = category._meta.get_field('name').verbose_name
        self.assertEquals(field_label, 'Имя категории')

    def test_name_max_length(self):
        category = Category.objects.get(id=1)
        max_length = category._meta.get_field('name').max_length
        self.assertEquals(max_length, 255)

    def test_get_absolute_url(self):
        category = Category.objects.get(id=1)
        # This will also fail if the urlconf is not defined.
        self.assertEquals(category.get_absolute_url(), '/category/refrigerators/')

