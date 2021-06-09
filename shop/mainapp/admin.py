# from PIL import Image

from django.forms import ModelChoiceField, ModelForm, ValidationError
from django.contrib import admin
# from django.utils.safestring import mark_safe

from .models import *


# class RefrigeratorAdminForm(ModelForm):
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.fields['image'].help_text = mark_safe(
#             """<span style="color:green; font-size:14px;">Минимальное разрешение для изображения {}x{},
#             при загрузке с разрешением больше {}x{} изображение будет обрезано</span>
#             """.format(
#                 *Product.MIN_RESOLUTION, *Product.MAX_RESOLUTION)
#         )
#
#     def clean_image(self):
#         image = self.cleaned_data['image']
#         img = Image.open(image)
#         min_height, min_width = Product.MIN_RESOLUTION
#         max_height, max_width = Product.MAX_RESOLUTION
#         if image.size > Product.MAX_IMAGE_SIZE:
#             raise ValidationError('Размер изображения превышает максимум (3MB)!')
#         if img.height < min_height or img.width < min_width:
#             raise ValidationError('Разрешение загруженного изображения меньше минимального!')
#         if img.height > max_height or img.width > max_width:
#             raise ValidationError('Разрешение загруженного изображения больше максимального!')
#         return image


class DishwasherAdminForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = kwargs.get('instance')
        if isinstance(self, Dishwasher):
            if not instance.drying:
                self.fields['drying_type'].widget.attrs.update({
                    'readonly': True, 'style': 'background: lightgrey;'
                })

    def clean(self):
        if not self.cleaned_data['drying']:
            self.cleaned_data['drying_type'] = None
        return self.cleaned_data


class RefrigeratorAdmin(admin.ModelAdmin):
    # form = RefrigeratorAdminForm

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'category':
            return ModelChoiceField(Category.objects.filter(slug='refrigerators'))
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class WasherAdmin(admin.ModelAdmin):

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'category':
            return ModelChoiceField(Category.objects.filter(slug='washers'))
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class DishwasherAdmin(admin.ModelAdmin):
    change_form_template = 'admin.html'
    form = DishwasherAdminForm

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'category':
            return ModelChoiceField(Category.objects.filter(slug='dishwashers'))
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


admin.site.register(Category)
admin.site.register(Refrigerator, RefrigeratorAdmin)
admin.site.register(Washer, WasherAdmin)
admin.site.register(Dishwasher, DishwasherAdmin)
admin.site.register(CartProduct)
admin.site.register(Cart)
admin.site.register(Customer)
admin.site.register(Order)
