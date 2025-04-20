"""
Проверка на активного пользователя выполняется автоматически,
так как в настройках проекта указано:

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}

При значении `is_active=False` пользователь считается деактивированным и не может
пройти аутентификацию через API, даже если введены корректные учетные данные
"""

from rest_framework import permissions


class IsProfileOwner(permissions.BasePermission):
    """ Проверка на владельца профиля """
    def has_object_permission(self, request, view, obj):
        return obj == request.user


class IsActiveEmployeeOrAdmin(permissions.BasePermission):
    """ Проверка на активного сотрудника и администратора """
    def has_permission(self, request, view):
        user = request.user
        return user.is_active and (user.groups.filter(name='employee').exists() or user.is_staff)


class CanViewUserProfile(permissions.BasePermission):
    """ Проверка на возможность просмотра профиля:

    – Сотрудник и админ могут просматривать любой профиль
    – Обычный пользователь может просматривать только свой
    """

    def has_object_permission(self, request, view, obj):
        user = request.user
        if obj == user:
            return True  # владелец профиля имеет доступ на чтение
        return user.groups.filter(name='employee').exists() or user.is_staff
