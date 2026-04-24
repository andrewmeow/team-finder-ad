from django.db import models
from users.models import User

CHOICES = (
    ('open', 'Открыт'),
    ('closed', 'Закрыт')
)


class Skill(models.Model):
    name = models.CharField(max_length=124)

    def __str__(self):
        return self.name


class Project(models.Model):
    name = models.CharField('Название', max_length=200)
    description = models.TextField('Описание')
    owner = models.ForeignKey(
        User,
        related_name='owned_projects',
        on_delete=models.CASCADE,
        verbose_name='Автор проекта',
    )
    created_at = models.DateTimeField('Добавлено', auto_now_add=True)
    github_url = models.URLField(
        'Ссылка на GitHub', null=True, blank=True, max_length=500)
    status = models.CharField('Статус', max_length=6,
                              choices=CHOICES, default='open')
    participants = models.ManyToManyField(
        User,
        related_name='participated_projects',
        blank=True,
    )
    skills = models.ManyToManyField(
        Skill,
        blank=True,
        related_name='projects',
    )
