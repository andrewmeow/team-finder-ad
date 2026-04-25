import random
from io import BytesIO

from django.contrib.auth.models import AbstractUser
from django.contrib.staticfiles.finders import find
from django.core.files.base import ContentFile
from django.db import models
from PIL import Image, ImageDraw, ImageFont

from team_finder.constants import (USER_ABOUT_MAX_LENGTH,
                                   USER_GITHUB_URL_MAX_LENGTH,
                                   USER_NAME_MAX_LENGTH, USER_PHONE_MAX_LENGTH,
                                   USER_SURNAME_MAX_LENGTH)
from users.managers import TeamFinderUserManager


class User(AbstractUser):
    username = None
    email = models.EmailField('Email', unique=True)
    name = models.CharField('Имя', max_length=USER_NAME_MAX_LENGTH)
    surname = models.CharField('Фамилия', max_length=USER_SURNAME_MAX_LENGTH)
    avatar = models.ImageField(
        'Аватар', upload_to='users_avatars', blank=True)
    phone = models.CharField(
        'Телефон', max_length=USER_PHONE_MAX_LENGTH, blank=True)
    github_url = models.URLField(
        'Ссылка на профиль GitHub', blank=True, null=True, max_length=USER_GITHUB_URL_MAX_LENGTH)
    about = models.TextField(
        'Описание профиля', max_length=USER_ABOUT_MAX_LENGTH, blank=True)
    is_active = models.BooleanField('Активный', default=True)
    is_staff = models.BooleanField('Администратор', default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'surname']

    objects = TeamFinderUserManager()

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
