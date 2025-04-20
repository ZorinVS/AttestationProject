from rest_framework import serializers
from rest_framework.reverse import reverse

from users.models import User
from users.validators import validate_password


class UserSerializer(serializers.ModelSerializer):
    """ Сериализатор модели `User` """

    password = serializers.CharField(write_only=True, required=False, validators=[validate_password])

    class Meta:
        model = User
        fields = ('email', 'password', 'phone_number', 'city',)

    def create(self, validated_data):
        """ Создание пользователя с хешированием пароля """
        password = validated_data.pop('password', None)
        if not password:
            raise serializers.ValidationError({'password': 'Обязательное поле при создании пользователя.'})
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        """ Обновление данных пользователя """
        if 'password' in validated_data:
            set_password_url = reverse('users:set_password')
            msg = f'Изменение пароля недоступно через этот эндпоинт. Используйте {set_password_url}.'
            raise serializers.ValidationError({'password': msg})
        return super().update(instance, validated_data)


class ChangePasswordSerializer(serializers.Serializer):
    """ Сериализатор для смены пароля """

    old_password = serializers.CharField(max_length=128, required=True)
    new_password = serializers.CharField(max_length=128, required=True, validators=[validate_password])

    def validate(self, attrs):
        """ Валидация введенных паролей """
        # Валидация старого пароля
        user = self.context['user']
        if not user.check_password(attrs['old_password']):
            raise serializers.ValidationError({'old_password': 'Старый пароль указан неверно.'})
        # Валидация нового пароля
        if attrs['old_password'] == attrs['new_password']:
            raise serializers.ValidationError({'new_password': 'Новый пароль не должен совпадать со старым.'})
        return attrs
