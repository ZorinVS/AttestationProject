from django.core.management import BaseCommand, call_command

FIXTURE_PATHS = (
    'users/fixtures/groups_fixture.json',
    'users/fixtures/users_fixture.json',
    'electronics_network/fixtures/supply_chain_member_fixture.json',
    'electronics_network/fixtures/contact_info_fixture.json',
    'electronics_network/fixtures/product_fixture.json'
)
TEST_USER_EMAILS = [
    'superuser@email.com',
    'active.employee@email.com',
    'inactive.employee@email.com',
    'new.user@email.com',
]
TEST_USER_EMAILS_STRING = '\n    '.join(TEST_USER_EMAILS)
AUTH_DETAILS = f"""
📧: {TEST_USER_EMAILS_STRING}

🔐: qwerty78
""".strip()


class Command(BaseCommand):
    help = 'Наполняет базу тестовыми данными (пользователи, поставщики)'

    def handle(self, *args, **options):
        """ Обработчик команды """
        self.stdout.write(self.style.WARNING('Начало загрузки данных'))
        for fixture_path in FIXTURE_PATHS:
            call_command('loaddata', fixture_path)
        self.stdout.write(self.style.SUCCESS('Данные успешно загружены\n'))
        self.stdout.write(AUTH_DETAILS)  # вывод данных для авторизации
