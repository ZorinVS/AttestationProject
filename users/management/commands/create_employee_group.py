from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand
from django.db import IntegrityError


class Command(BaseCommand):
    help = 'Создает группу сотрудников'

    def handle(self, *args, **options):
        """ Обработчик команды """
        try:
            Group.objects.create(name='employee')
        except IntegrityError:
            pass
        self.stdout.write(self.style.SUCCESS("Группа 'employee' успешно создана!"))
