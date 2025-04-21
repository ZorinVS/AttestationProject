from django.contrib.auth.models import Group
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from electronics_network.models import ContactInfo, SupplyChainMember
from users.models import User


class SupplyChainMemberTestCase(APITestCase):

    def setUp(self):
        """ Подготовка данных для тестов """

        # Пользователи
        employee_group = Group.objects.create(name='employee')
        self.employee = User.objects.create(email='employee@test.api')
        self.employee.groups.add(employee_group)
        self.user = User.objects.create(email='user@test.api', is_active=False)

        # Поставщики
        self.suppliers = []
        self.new_supplier_data = {
            'name': 'NewFactory',
            'type': 'factory',
            'contact': {
                'email': 'new@test.api',
                'country': 'Country0',
                'city': 'City0',
                'street': 'Street0',
                'house_number': '1',
            }
        }
        self.members_data = [
            {
                'name': 'Factory1',
                'type': 'factory',
            },
            {
                'name': 'Factory2',
                'type': 'factory',
            },
        ]
        self.contacts_data = [
            {
                'email': 'supplier1@test.api',
                'country': 'Country1',
                'city': 'City1',
                'street': 'Street1',
                'house_number': 'A1',
            },
            {
                'email': 'supplier2@test.api',
                'country': 'Country2',
                'city': 'City2',
                'street': 'Street2',
                'house_number': 'A2',
            }
        ]
        for member_data, contact_data in zip(self.members_data, self.contacts_data):  # создание поставщиков
            supplier = SupplyChainMember.objects.create(user=self.employee, **member_data)
            ContactInfo.objects.create(network_member=supplier, **contact_data)
            self.suppliers.append(supplier)

    def test_create(self):
        """ Тест создания участника поставки """
        url = reverse('electronics_network:supplier-list')

        # === 1. Тест новым пользователем, который не является сотрудником ===
        self.client.force_authenticate(user=self.user)
        response = self.client.post(url, data=self.new_supplier_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.json()['detail'], 'У вас недостаточно прав для выполнения данного действия.')

        # === 2. Тест активным сотрудником ===
        self.client.force_authenticate(user=self.employee)
        response = self.client.post(url, data=self.new_supplier_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            first=response.json()['name'],
            second=self.new_supplier_data['name']
        )

    def test_list(self):
        """ Тест просмотра списка участников """
        url = reverse('electronics_network:supplier-list')
        self.client.force_authenticate(user=self.employee)

        # === 1. Тест получения всего списка ===
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['count'], len(self.suppliers))
        self.assertEqual(response.json()['next'], None)

        # === 2. Тест получения списка с параметром `page_size=1`
        response = self.client.get(url, query_params={'page_size': 1})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()['results']), 1)
        self.assertEqual(response.json()['results'][0]['name'], 'Factory1')
        self.assertEqual(response.json()['next'], 'http://testserver/api/suppliers/?page=2&page_size=1')

        # === 3. Тест получения списка участников из страны 'Country2'
        response = self.client.get(url, query_params={'page_size': 1, 'country': 'Country2'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()['results']), 1)
        self.assertEqual(response.json()['results'][0]['name'], 'Factory2')
        self.assertEqual(response.json()['next'], None)

    def test_retrieve(self):
        """ Тест просмотра данных участника """
        url = reverse('electronics_network:supplier-detail', args=(self.suppliers[0].pk,))

        # === 1. Тест новым пользователем, который не является сотрудником ===
        self.client.force_authenticate(user=self.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.json()['detail'], 'У вас недостаточно прав для выполнения данного действия.')

        # === 2. Тест активным сотрудником ===
        self.client.force_authenticate(user=self.employee)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['name'], 'Factory1')

    def test_update(self):
        """ Тест полного обновления данных """
        url = reverse('electronics_network:supplier-detail', args=(self.suppliers[0].pk,))
        self.client.force_authenticate(user=self.employee)

        # === 1. Тест провального обновления ===
        new_data = self.members_data[0].copy()
        new_data['name'] = 'New name'
        response = self.client.put(url, data=new_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(), {'contact': ['Обязательное поле.']})

        # === 2. Тест успешного обновления ===
        new_data['contact'] = self.contacts_data[0]
        response = self.client.put(url, data=new_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['name'], 'New name')

    def test_partial_update(self):
        """ Тест частичного обновления данных """
        url = reverse('electronics_network:supplier-detail', args=(self.suppliers[0].pk,))
        self.client.force_authenticate(user=self.employee)

        # === 1. Тест провального обновления ===
        new_data = self.members_data[0].copy()
        new_data['name'] = 'Factory2'
        response = self.client.patch(url, data=new_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            first=response.json()['name'][0],
            second='участник цепочки поставок с таким Название участника сети продаж уже существует.'
        )

        # === 2. Тест успешного обновления ===
        new_data['name'] = 'New name'
        response = self.client.patch(url, data=new_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['name'], 'New name')

    def test_destroy(self):
        """ Тест удаления участника """
        url = reverse('electronics_network:supplier-detail', args=(self.suppliers[0].pk,))

        # === 1. Тест новым пользователем, который не является сотрудником ===
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.json()['detail'], 'У вас недостаточно прав для выполнения данного действия.')

        # === 2. Тест активным сотрудником ===
        self.client.force_authenticate(user=self.employee)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
