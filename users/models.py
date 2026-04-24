from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
import random
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from django.core.files.base import ContentFile
from django.contrib.staticfiles.finders import find


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('Email обязателен')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    username = None
    email = models.EmailField('Email', unique=True)
    name = models.CharField('Имя', max_length=124)
    surname = models.CharField('Фамилия', max_length=124)
    avatar = models.ImageField(
        'Аватар', upload_to='users_avatars', blank=True)
    phone = models.CharField('Телефон', max_length=12, blank=True)
    github_url = models.URLField(
        'Ссылка на профиль GitHub', blank=True, null=True, max_length=500)
    about = models.TextField('Описание профиля', max_length=256, blank=True)
    is_active = models.BooleanField('Активный', default=True)
    is_staff = models.BooleanField('Администратор', default=False)

    objects = CustomUserManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'surname']

    def save(self, *args, **kwargs):
        if not self.avatar:
            self.avatar = self.generate_avatar()
        super().save(*args, **kwargs)

    def generate_avatar(self):
        font_path = find('fonts/Neue_Haas_Grotesk_Display_Pro_75_Bold.otf')
        try:
            font = ImageFont.truetype(font_path, 130)
        except IOError:
            font = ImageFont.load_default()
        bg_color = (
            random.randint(100, 200),
            random.randint(100, 200),
            random.randint(100, 200)
        )
        letter = self.name[0].upper() if self.name else '?'
        img = Image.new('RGB', (200, 200), color=bg_color)
        draw = ImageDraw.Draw(img)

        bbox = draw.textbbox((0, 0), letter, font=font)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]
        x = (200 - w) / 2 - bbox[0]
        y = (200 - h) / 2 - bbox[1]
        draw.text((x, y), letter, fill='white', font=font)

        buffer = BytesIO()
        img.save(buffer, format='PNG')
        filename = f'avatar_{self.email}.png'
        return ContentFile(buffer.getvalue(), name=filename)
