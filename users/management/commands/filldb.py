from django.core.management.base import BaseCommand

from projects.models import Project, Skill
from users.models import User


class Command(BaseCommand):
    help = 'Заполняет базу двумя тестовыми пользователями и проектами'

    def handle(self, *args, **options):
        # Создаём двух пользователей
        alice = User.objects.create_user(
            email='alice@example.com',
            password='strongpassword1',
            name='Алиса',
            surname='Иванова',
            github_url='https://github.com/nikita-voronin',
            phone='+79991234567',
            about='Frontend-разработчик, люблю React',
        )
        bob = User.objects.create_user(
            email='bob@example.com',
            password='strongpassword2',
            name='Боб',
            surname='Петров',
            phone='+79997654321',
            about='Backend-разработчик, Python/Django',
        )

        # Пара навыков
        skill_python, _ = Skill.objects.get_or_create(name='Python')
        skill_react, _ = Skill.objects.get_or_create(name='React')

        # Проект Алисы
        project_alice = Project.objects.create(
            name='Сайт портфолио',
            description='Современное портфолио на React с анимациями',
            owner=alice,
            github_url='https://github.com/linguabot/ai-tutor',
            status='open',
        )
        project_alice.skills.add(skill_react)

        # Проект Боба
        project_bob = Project.objects.create(
            name='API для блога',
            description='REST API на Django Rest Framework',
            owner=bob,
            status='open',
        )
        project_bob.skills.add(skill_python)

        # Боб подписывается на проект Алисы
        project_alice.participants.add(bob)

        self.stdout.write(self.style.SUCCESS(
            'База успешно заполнена тестовыми данными'))
