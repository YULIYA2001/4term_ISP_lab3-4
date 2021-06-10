from django.forms import ModelChoiceField, ModelForm
from django.contrib import admin

from .models import *


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
