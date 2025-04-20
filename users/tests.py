from django.contrib.auth.models import Group
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from users.models import User


class UserTestCase(APITestCase):

    def setUp(self):
        """ Подготовка данных для тестов """
        self.password = 'qwerty123'
        self.user_emails = [
            'user@test.api',
            'inactive.employee@test.api',
            'employee@test.api',
            'admin@test.api',
        ]
        self.employee_group = Group.objects.create(name='employee')
        self.users = []

        # Создание пользователей
        for email in self.user_emails:
            user_data = {'email': email, 'password': self.password}
            if 'admin' in email:  # добавление администратора
                user_data.update({'is_staff': True})
            user = User.objects.create_user(**user_data)  # создание аккаунта
            if 'employee' in email:  # добавления пользователя в группу сотрудников
                user.groups.add(self.employee_group)
            if 'inactive' in email:  # перевод сотрудника в неактивный статус
                user.is_active = False

            user.save()
            self.users.append(user)

    def test_create(self):
        """ Тест регистрации пользователя """
        url = reverse('users:user_create')

        # === 1. Тест успешного создания нового пользователя ===
        user_data = {'email': 'new.user@test.api', 'password': self.password}
        response = self.client.post(url, data=user_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # === 2. Тест провального создания пользователя с почтой, которая уже использовалась ===
        user_data.update({'email': self.get_user_email('user')})
        response = self.client.post(url, data=user_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            first=response.json()['email'][0],
            second='пользователь с таким Email уже существует.',
        )

    def test_getting_jwt(self):
        """ Тест авторизации пользователя """
        url = reverse('users:token_obtain_pair')

        # === 1. Тест успешной авторизации активным пользователем ===
        user_data = {'email': self.get_user_email('user'), 'password': self.password}  # user@test.api
        response = self.client.post(url, data=user_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # === 2. Тест провальной авторизации неактивным сотрудником ===
        user_data.update({'email': self.get_user_email('inactive')})  # inactive.employee@test.api
        response = self.client.post(url, data=user_data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(
            first=response.json()['detail'],
            second='Не найдено активной учетной записи с указанными данными',
        )

    def test_retrieve(self):
        """ Тест просмотра данных профиля """
        user = self.users[self.get_user_index('user')]  # пользователь не состоящий в группе сотрудников
        url = reverse('users:user_detail', args=(user.pk,))  # URL для получения данных профиля пользователя

        # === 1. Тест неавторизованным пользователем ===
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(
            first=response.json()['detail'],
            second='Учетные данные не были предоставлены.',
        )

        # === 2. Тесты пользователем, который еще не состоит в группе сотрудников ===
        # Авторизация пользователем user@test.api
        self.client.force_authenticate(user=user)
        # --- Успешный просмотр своего профиля ---
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            first=response.json()['email'],
            second=user.email,  # user@test.api
        )
        # --- Провальный просмотр чужого профиля ---
        url = reverse('users:user_detail', args=(user.pk + 1,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            first=response.json()['detail'],
            second='У вас недостаточно прав для выполнения данного действия.',
        )

        # === 3. Тест успешного просмотра чужого профиля активным сотрудником ===
        user = self.users[self.get_user_index('employee')]  # пользователь являющийся активным сотрудником
        self.client.force_authenticate(user=user)  # авторизация пользователем employee@test.api
        url = reverse('users:user_detail', args=(user.pk + 1,))  # просмотр чужого профиля
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            first=response.json()['email'],
            second=self.user_emails[self.get_user_index('employee') + 1],  # admin@test.api
        )

        # === 4. Тест успешного просмотра чужого профиля админом ===
        user = self.users[self.get_user_index('admin')]  # пользователь являющийся админом
        self.client.force_authenticate(user=user)  # авторизация пользователем admin@test.api
        url = reverse('users:user_detail', args=(user.pk - 1,))  # просмотр чужого профиля
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            first=response.json()['email'],
            second=self.user_emails[self.get_user_index('admin') - 1],  # employee@test.api
        )

    def test_update(self):
        """ Тест полного обновления данных """
        user = self.users[self.get_user_index('user')]
        self.client.force_authenticate(user=user)  # авторизация пользователем user@test.api
        self.assertEqual(user.city, None)  # информация о городе в профиле отсутствует
        url = reverse('users:user_detail', args=(user.pk,))

        # === 1. Тест провального обновления своего профиля ===
        user_data = {'city': 'Самара'}
        response = self.client.put(url, data=user_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            first=response.json(),
            second={'email': ['Обязательное поле.']},
        )

        # === 2. Тест успешного обновления своего профиля
        user_data.update({'email': user.email})
        response = self.client.put(url, data=user_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            first=response.json()['city'],
            second=user_data['city'],
        )

        # === 3. Тест попытки администратора обновить чужой профиль ===
        admin = self.users[self.get_user_index('admin')]
        self.client.force_authenticate(user=admin)  # авторизация пользователем admin@test.api
        response = self.client.put(url, data=user_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            first=response.json()['detail'],
            second='У вас недостаточно прав для выполнения данного действия.'
        )

    def test_partial_update(self):
        """ Тест частичного обновления данных """
        user = self.users[self.get_user_index('user')]
        self.client.force_authenticate(user=user)  # авторизация пользователем user@test.api
        self.assertEqual(user.city, None)  # информация о городе в профиле отсутствует
        url = reverse('users:user_detail', args=(user.pk,))

        # === Успешный тест частичного обновления своего профиля
        user_data = {'city': 'Самара'}
        response = self.client.patch(url, data=user_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            first=response.json()['city'],
            second=user_data['city'],
        )

        # === Тест попытки обновить пароль ===
        user_data = {'password': 'qwerty0987'}
        response = self.client.patch(url, data=user_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            first=response.json()['password'],
            second='Изменение пароля недоступно через этот эндпоинт. Используйте /api/users/set_password/.',
        )

    def test_destroy(self):
        """ Тест удаления пользователя """
        user = self.users[self.get_user_index('user')]
        user_email = user.email
        self.client.force_authenticate(user=user)  # авторизация пользователем user@test.api
        url = reverse('users:user_detail', args=(user.pk,))

        # === 1. Тест провального удаления своего профиля обычным пользователем ===
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            first=response.json()['detail'],
            second='У вас недостаточно прав для выполнения данного действия.'
        )

        # === 2. Тест успешного удаления чужого профиля администратором ===
        admin = self.users[self.get_user_index('admin')]
        self.client.force_authenticate(user=admin)  # авторизация пользователем admin@test.api
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        does_user_exist = User.objects.filter(email=user_email).exists()
        self.assertEqual(does_user_exist, False)

    def test_set_password(self):
        """ Тест смены пароля """
        url = reverse('users:set_password')
        user = self.users[self.get_user_index('user')]
        self.client.force_authenticate(user=user)  # авторизация пользователем user@test.api

        # === 1. Тест успешной смены пароля ===
        data = {
            'old_password': self.password,
            'new_password': 'poiuy123',
        }
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            first=response.json()['detail'],
            second='Пароль успешно изменён.',
        )

        # === 2. Тест смены пароля с использованием старого пароля ===
        data.update({'old_password': data['new_password']})
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            first=response.json()['new_password'][0],
            second='Новый пароль не должен совпадать со старым.',
        )

        # === 3. Тест смены пароля с использованием короткого пароля ===
        data.update({'new_password': 'q1'})
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            first=response.json()['new_password'][0],
            second='Длина пароля не может быть меньше 8 символов.',
        )

        # === 4. Тест смены пароля с использованием запрещенных символов ===
        data.update({'new_password': 'q-q-q-qq-q-q-qq1'})
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            first=response.json()['new_password'][0],
            second='Пароль должен состоять только из буквенно-цифровых символов.',
        )

        # === 5. Тест смены пароля с использованием пароля, состоящего только из цифр ===
        data.update({'new_password': '88888888'})
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            first=response.json()['new_password'][0],
            second='Пароль должен содержать хотя бы один латинский символ.',
        )

        # === 6. Тест смены пароля с использованием пароля, состоящего только из букв ===
        data.update({'new_password': 'qqqqqqqq'})
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            first=response.json()['new_password'][0],
            second='Пароль должен содержать хотя бы одну цифру.',
        )

        # === 7. Тест смены пароля с использованием кириллицы ===
        data.update({'new_password': 'qwукен12'})
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            first=response.json()['new_password'][0],
            second='Пароль не может содержать кириллицу.',
        )

    # ======= Вспомогательные методы =======

    @staticmethod
    def _get_user_type(user_email):
        """ Получение типа пользователя по Email """
        return user_email.split('.')[0].split('@')[0]

    def get_user_index(self, user_type):
        """ Функция возвращающая индекс пользователя в зависимости от его типа:

        · user – пользователь, который еще не состоит в группе сотрудников
        · inactive – неактивный сотрудник
        · employee – активный сотрудник
        · admin – администратор
        """
        user_indexes = {self._get_user_type(email): i for i, email in enumerate(self.user_emails)}
        return user_indexes[user_type]

    def get_user_email(self, user_type):
        """ Функция возвращающая Email пользователя в зависимости от его типа:

        · user – пользователь, который еще не состоит в группе сотрудников
        · inactive – неактивный сотрудник
        · employee – активный сотрудник
        · admin – администратор
        """
        index = self.get_user_index(user_type)
        return self.user_emails[index]
