from django import forms
from django.contrib.auth.models import User
from datetime import date

from .models import Order


class OrderForm(forms.ModelForm):
    phone = forms.RegexField(regex=r'^\+375\((17|29|33|44)\)[0-9]{7}$',
                             required=True, help_text="формат ввода: +375(00)0000000",
                             error_messages={'invalid': "Неверный формат ввода"})
    address = forms.CharField(required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['order_date'].label = 'Дата получения заказа'
        self.fields['phone'].label = 'Номер телефона'
        self.fields['address'].label = 'Адрес доставки'

    order_date = forms.DateField(widget=forms.TextInput(attrs={'type': 'date'}))

    def clean_order_date(self):
        order_date = self.cleaned_data['order_date']
        if order_date < date.today():
            raise forms.ValidationError(f'Введенная дата является прошедшей.')
        return order_date

    def clean_address(self):
        address = self.cleaned_data['address']
        if not address:
            raise forms.ValidationError(f'Введите адрес.')
        return address

    class Meta:
        model = Order
        fields = (
            'phone', 'buying_type', 'address', 'order_date', 'comment'
            # 'first_name', 'last_name', 'phone', 'address', 'buying_type', 'order_date', 'comment'
        )


class LoginForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'Логин'
        self.fields['password'].label = 'Пароль'

    def clean(self):
        username = self.cleaned_data['username']
        password = self.cleaned_data['password']
        if not User.objects.filter(username=username).exists():
            raise forms.ValidationError(f'Пользователь с логином {username} не найден.')
        user = User.objects.filter(username=username).first()
        if user:
            if not user.check_password(password):
                raise forms.ValidationError('Неверный пароль')
        return self.cleaned_data

    class Meta:
        model = User
        fields = ['username', 'password']


class RegistrationForm(forms.ModelForm):
    confirm_password = forms.CharField(widget=forms.PasswordInput)
    password = forms.CharField(widget=forms.PasswordInput)
    phone = forms.RegexField(regex=r'^\+375\((17|29|33|44)\)[0-9]{7}$',
                             required=False, help_text="формат ввода: +375(00)0000000",
                             error_messages={'invalid': "Неверный формат ввода"})
    address = forms.CharField(required=False)
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'Логин'
        self.fields['password'].label = 'Пароль'
        self.fields['confirm_password'].label = 'Подтвердите пароль'
        self.fields['phone'].label = 'Номер телефона'
        self.fields['first_name'].label = 'Имя'
        self.fields['last_name'].label = 'Фамилия'
        self.fields['address'].label = 'Адрес'
        self.fields['email'].label = 'Электронная почта'

    def clean_email(self):
        email = self.cleaned_data['email']
        #domain = email.split('.')[-1]
        #if domain is not ['com']:
        #    raise forms.ValidationError(f'Регистрация для домена "{domain}" невозможна')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(f'Данный почтовый адрес уже зарегистрирован')
        return email

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError(f'Имя {username} уже используется')
        return username

    def clean(self):
        password = self.cleaned_data['password']
        confirm_password = self.cleaned_data['confirm_password']
        if confirm_password != password:
            raise forms.ValidationError(f'Пароли не совпадают')
        return self.cleaned_data

    class Meta:
        model = User
        fields = [
            'username', 'password', 'confirm_password', 'first_name', 'last_name', 'address', 'phone', 'email'
        ]
