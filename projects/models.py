from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse

from team_finder.constants import (OPEN_STATUS, PROJECT_GITHUB_URL_MAX_LENGTH,
                                   PROJECT_NAME_MAX_LENGTH,
                                   PROJECT_STATUS_MAX_LENGTH,
                                   SKILL_NAME_MAX_LENGTH, STATUS_CHOICES)

User = get_user_model()


class Skill(models.Model):
    name = models.CharField('Название', max_length=SKILL_NAME_MAX_LENGTH)

    class Meta:
        verbose_name = 'навык'
        verbose_name_plural = 'Навыки'

    def __str__(self):
        return self.name


class Project(models.Model):
    name = models.CharField('Название', max_length=PROJECT_NAME_MAX_LENGTH)
    description = models.TextField('Описание')
    owner = models.ForeignKey(
        User,
        related_name='owned_projects',
        on_delete=models.CASCADE,
        verbose_name='Автор проекта',
    )
    created_at = models.DateTimeField('Добавлено', auto_now_add=True)
    github_url = models.URLField(
        'Ссылка на GitHub', null=True, blank=True, max_length=PROJECT_GITHUB_URL_MAX_LENGTH)
    status = models.CharField('Статус', max_length=PROJECT_STATUS_MAX_LENGTH,
                              choices=STATUS_CHOICES, default=OPEN_STATUS)
    participants = models.ManyToManyField(
        User,
        related_name='participated_projects',
        blank=True,
        verbose_name='Участники',
    )
    skills = models.ManyToManyField(
        Skill,
        blank=True,
        related_name='projects',
        verbose_name='Необходимые навыки',
    )

    class Meta:
        verbose_name = 'проект'
        verbose_name_plural = 'Проекты'

    def get_absolute_url(self):
        return reverse('projects:project-details', kwargs={'pk': self.pk})

    def __str__(self):
        return self.name
