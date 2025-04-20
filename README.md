# Онлайн платформа-торговой сети электроники

## 1. Реализована модель сети по продаже электроники.

Сеть представлять собой иерархическую структуру из трех уровней:

    - завод;
    - розничная сеть;
    - индивидуальный предприниматель.

Каждое звено сети ссылается только на одного поставщика оборудования (не обязательно предыдущего по иерархии). 
Важно отметить, что уровень иерархии определяется не названием звена, а отношением к остальным элементам сети, т.е. 
завод всегда находится на уровне 0, а если розничная сеть относится напрямую к заводу, минуя остальные звенья, ее уровень — 1.


## 2. Каждое звено сети обладает следующими элементами:

- **Название**.
- **Контакты**:
  - email,
  - страна,
  - город,
  - улица,
  - номер дома.
- **Продукты**:
  - название,
  - модель,
  - дата выхода продукта на рынок.
- **Поставщик** (предыдущий по иерархии объект сети).
- **Задолженность перед поставщиком** в денежном выражении с точностью до копеек.
- **Время создания** (заполняется автоматически при создании).


## 3. Реализован вывод в админ-панели созданных объектов.

На странице объекта сети добавлены:
- ссылка на «Поставщика»;
- фильтр по названию города;
- admin action, очищающий задолженность перед поставщиком у выбранных объектов.


## 4. Используя DRF, создан набор представлений:

- CRUD для модели поставщика (запрещено обновление через API поля «Задолженность перед поставщиком»).
- Добавлена возможность фильтрации объектов по определенной стране.
- CRUD для модели продукта.
- Добавлена пагинация для получения списков объектов.
- Реализован набор представлений для управления пользователями:
  - Регистрация нового пользователя: `POST /api/users/register/`
  - Получение JWT токенов (вход): `POST /api/users/login/`
  - Обновление access токена: `POST /api/users/token/refresh/`
  - Смена пароля текущего пользователя: `POST /api/users/set_password/`
  - Получение / редактирование / удаление пользователя по ID: `GET | PUT | PATCH | DELETE /api/users/<int:pk>/`
    - `GET` доступен владельцу, администратору и другим сотрудникам. 
    - `PUT | PATCH` доступен только владельцу профиля. 
    - `DELETE` доступен только администратору.


## 5. Настроены права доступа к API

Только активные сотрудники имеют доступ к API.


## 6. Настроена документация API

- **swagger:** http://localhost:8000/swagger/
- **redoc:** http://localhost:8000/redoc/


## 7. Написаны тесты для API

В проекте реализованы тесты для API с использованием `APITestCase` из `rest_framework.test`.  
Покрытие кода рассчитывается с помощью библиотеки `coverage`.

### Команда для запуска тестов с покрытием:
```sh
coverage run --source='.' manage.py test && coverage report
```

### Пример результата покрытия:

| Name                                                                             | Stmts   | Miss   | Cover   |
|----------------------------------------------------------------------------------|---------|--------|---------|
| config/__init__.py                                                               | 0       | 0      | 100%    |
| config/asgi.py                                                                   | 4       | 4      | 0%      |
| config/settings.py                                                               | 27      | 0      | 100%    |
| config/urls.py                                                                   | 11      | 1      | 91%     |
| config/wsgi.py                                                                   | 4       | 4      | 0%      |
| electronics_network/__init__.py                                                  | 0       | 0      | 100%    |
| electronics_network/admin.py                                                     | 30      | 6      | 80%     |
| electronics_network/apps.py                                                      | 4       | 0      | 100%    |
| electronics_network/filters.py                                                   | 7       | 0      | 100%    |
| electronics_network/management/__init__.py                                       | 0       | 0      | 100%    |
| electronics_network/management/commands/__init__.py                              | 0       | 0      | 100%    |
| electronics_network/management/commands/fill_with_data.py                        | 13      | 13     | 0%      |
| electronics_network/migrations/0001_initial.py                                   | 6       | 0      | 100%    |
| electronics_network/migrations/0002_initial.py                                   | 7       | 0      | 100%    |
| electronics_network/migrations/0003_remove_supplychainmember_contact_and_more.py | 5       | 0      | 100%    |
| electronics_network/migrations/__init__.py                                       | 0       | 0      | 100%    |
| electronics_network/models.py                                                    | 47      | 4      | 91%     |
| electronics_network/paginators.py                                                | 5       | 0      | 100%    |
| electronics_network/serializers.py                                               | 48      | 7      | 85%     |
| electronics_network/services.py                                                  | 6       | 5      | 17%     |
| electronics_network/tests.py                                                     | 90      | 0      | 100%    |
| electronics_network/urls.py                                                      | 8       | 0      | 100%    |
| electronics_network/views.py                                                     | 31      | 1      | 97%     |
| manage.py                                                                        | 11      | 2      | 82%     |
| users/__init__.py                                                                | 0       | 0      | 100%    |
| users/admin.py                                                                   | 8       | 0      | 100%    |
| users/apps.py                                                                    | 4       | 0      | 100%    |
| users/management/__init__.py                                                     | 0       | 0      | 100%    |
| users/management/commands/__init__.py                                            | 0       | 0      | 100%    |
| users/management/commands/create_employee_group.py                               | 11      | 11     | 0%      |
| users/migrations/0001_initial.py                                                 | 6       | 0      | 100%    |
| users/migrations/__init__.py                                                     | 0       | 0      | 100%    |
| users/models.py                                                                  | 30      | 5      | 83%     |
| users/permissions.py                                                             | 14      | 0      | 100%    |
| users/serializers.py                                                             | 33      | 2      | 94%     |
| users/tests.py                                                                   | 152     | 0      | 100%    |
| users/urls.py                                                                    | 6       | 0      | 100%    |
| users/validators.py                                                              | 13      | 0      | 100%    |
| users/views.py                                                                   | 28      | 0      | 100%    |
| **TOTAL**                                                                        | **669** | **65** | **90%** |
