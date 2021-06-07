# Generated by Django 3.2.4 on 2021-06-07 16:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0005_auto_20210607_1535'),
    ]

    operations = [
        migrations.CreateModel(
            name='Dishwasher',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255, verbose_name='Наименование')),
                ('slug', models.SlugField(unique=True)),
                ('image', models.ImageField(upload_to='', verbose_name='Изображение')),
                ('description', models.TextField(null=True, verbose_name='Описание')),
                ('price', models.DecimalField(decimal_places=2, max_digits=9, verbose_name='Цена')),
                ('max_load', models.CharField(max_length=255, verbose_name='Максимальная загрузка (комплекты посуды)')),
                ('drying', models.BooleanField(default=True)),
                ('drying_type', models.CharField(max_length=255, verbose_name='Тип сушки')),
                ('number_of_programs', models.CharField(max_length=255, verbose_name='Количество программ')),
                ('noise_level', models.CharField(max_length=255, verbose_name='Уровень шума')),
                ('shortest_program', models.CharField(max_length=255, verbose_name='Время самой короткой программы')),
                ('water_consumption_per_cycle', models.CharField(max_length=255, verbose_name='Расход воды за цикл')),
                ('control', models.CharField(max_length=255, verbose_name='Тип управления')),
                ('child_lock', models.BooleanField(default=True)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mainapp.category', verbose_name='Категория')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]