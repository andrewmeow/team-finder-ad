import re
from urllib.parse import urlparse

from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import AuthenticationForm, UserChangeForm
from django.core.exceptions import ValidationError

from users.models import User

GITHUB_URL = 'github.com'


def clean_github(self):
    url = self.cleaned_data.get(GITHUB_URL)
    if not url:
        return url

    parsed = urlparse(url)

    if parsed.scheme not in ('http', 'https'):
        raise ValidationError(
            'Некорректный URL. Используйте http:// или https://')

    if not (parsed.netloc == GITHUB_URL or parsed.netloc.endswith(GITHUB_URL)):
        raise ValidationError(f'Ссылка должна вести на GitHub {GITHUB_URL}')

    return url


class TeamFinderUserManager(AuthenticationForm):
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={'autofocus': True}),
    )
    password = forms.CharField(
        label='Пароль',
        strip=False,
        widget=forms.PasswordInput,
    )

    def __init__(self, request=None, *args, **kwargs):
        super().__init__(request=request, *args, **kwargs)
        # Удаляем поле username, оставляем наши поля
        if 'username' in self.fields:
            del self.fields['username']

    def clean(self):
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')

        if email is not None and password:
            self.user_cache = authenticate(
                self.request, username=email, password=password)
            if self.user_cache is None:
                raise forms.ValidationError(
                    'Неверный адрес электронной почты или пароль.',
                    code='invalid_login',
                )
            else:
                self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data


class SignUpForm(forms.ModelForm):
    password = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput,
    )

    class Meta:
        model = User
        fields = ('email', 'name', 'surname', 'phone', 'github_url', 'about')
        labels = {
            'email': 'Email',
            'name': 'Имя',
            'surname': 'Фамилия',
            'phone': 'Номер телефона',
            'github_url': 'Ссылка на профиль GitHub',
            'about': 'О себе',
        }

    def clean_github_url(self):
        return clean_github(self)

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if not phone:
            return phone
        if not re.match(r'^(\+7\d{10}|8\d{10})$', phone):
            raise ValidationError(
                'Номер телефона должен быть в формате +7XXXXXXXXXX или 8XXXXXXXXXX'
            )
        if phone.startswith('8'):
            normalized = '+7' + phone[1:]
        else:
            normalized = phone
        if User.objects.filter(phone__in=[phone, normalized]).exists():
            raise ValidationError(
                'Пользователь с таким номером уже существует')
        return normalized

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user


class ProfileEditForm(UserChangeForm):
    class Meta:
        model = User
        fields = ('name', 'surname', 'avatar', 'phone', 'github_url', 'about')
        labels = {
            'email': 'Электронная почта',
            'name': 'Имя',
            'surname': 'Фамилия',
            'avatar': 'Аватар',
            'phone': 'Номер телефона',
            'github_url': 'Ссылка на профиль GitHub',
            'about': 'О себе',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'password' in self.fields:
            del self.fields['password']
        self.fields['avatar'].widget = forms.FileInput()

    def clean_github_url(self):
        return clean_github(self)

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if not phone:
            return phone

        if not re.match(r'^(\+7\d{10}|8\d{10})$', phone):
            raise ValidationError(
                'Номер телефона должен быть в формате +7XXXXXXXXXX или 8XXXXXXXXXX (X — цифры)'
            )

        if phone.startswith('8'):
            normalized = '+7' + phone[1:]
        else:
            normalized = phone
        existing = User.objects.filter(
            phone__in=[phone, normalized]
        )
        if self.instance and self.instance.pk:
            existing = existing.exclude(pk=self.instance.pk)

        if existing.exists():
            raise ValidationError(
                'Пользователь с таким номером телефона уже существует')

        return normalized
