from django import template
from django.utils.safestring import mark_safe

from mainapp.models import Dishwasher

register = template.Library()

TABLE_HEAD = """
                <table class="table">
                  <tbody>
             """

TABLE_TAIL = """
                  </tbody>
                </table>
             """

TABLE_CONTENT = """
                    <tr>
                      <td>{name}</td>
                      <td>{value}</td>
                    </tr>
                """

PRODUCT_SPEC = {
    'refrigerator': {
        'Общий объем': 'overall_volume',
        'Полезный объем': 'useful_volume',
        'Тип управления': 'control',
        'Уровень шума': 'noise_level',
        'Количество полок': 'number_of_shelves',
        'Количество полок морозильной камеры': 'number_of_freezer_shelves'
    },
    'washer': {
        'Максимальный объем загрузки': 'max_loading',
        'Максимальная скорость отжима': 'max_spin_speed',
        'Количество программ стирки': 'number_of_programs',
        'Время самой короткой программы': 'shortest_program',
        'Расход электроэнергии за цикл': 'electricity_consumption_per_cycle',
        'Расход воды за цикл': 'water_consumption_per_cycle'
    },
    'dishwasher': {
        'Максимальная загрузка (комплекты посуды)': 'max_load',
        'Наличие сушки': 'drying',
        'Тип сушки': 'drying_type',
        'Количество программ': 'number_of_programs',
        'Уровень шума': 'noise_level',
        'Время самой короткой программы': 'shortest_program',
        'Расход воды за цикл': 'water_consumption_per_cycle',
        'Тип управления': 'control',
        'Защита от детей': 'child_lock'
    }
}


def get_product_spec(product, model_name):
    table_content = ''
    for name, value in PRODUCT_SPEC[model_name].items():
        value = getattr(product, value)
        if value is True:
            value = 'Да'
        elif value is False:
            value = 'Нет'
        table_content += TABLE_CONTENT.format(name=name, value=value)
    return table_content


# пользовательский фильтр
@register.filter
def product_spec(product):
    model_name = product.__class__._meta.model_name
    if isinstance(product, Dishwasher):
        if not product.drying:
            PRODUCT_SPEC['dishwasher'].pop('Тип сушки')
        else:
            PRODUCT_SPEC['dishwasher']['Тип сушки'] = 'drying_type'
    return mark_safe(TABLE_HEAD + get_product_spec(product, model_name) + TABLE_TAIL)