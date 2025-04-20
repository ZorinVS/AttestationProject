import re

from rest_framework import serializers


def validate_password(password):
    """ Проверяет, что пароль соответствует следующим требованиям безопасности:

    - Минимальная длина: не менее 8 символов
    - Состоит только из латинских букв и цифр (т.е. буквы английского алфавита и цифры)
    - Содержит хотя бы одну букву
    - Содержит хотя бы одну цифру
    - Не содержит кириллицу (русские буквы запрещены)
    """
    if len(password) < 8:
        raise serializers.ValidationError('Длина пароля не может быть меньше 8 символов.')
    if not password.isalnum():
        raise serializers.ValidationError('Пароль должен состоять только из буквенно-цифровых символов.')
    if not bool(re.search(r'\D', string=password)):
        raise serializers.ValidationError('Пароль должен содержать хотя бы один латинский символ.')
    if not bool(re.search(r'\d', string=password)):
        raise serializers.ValidationError('Пароль должен содержать хотя бы одну цифру.')
    if bool(re.search(r'[а-я]', string=password, flags=re.IGNORECASE)):
        raise serializers.ValidationError('Пароль не может содержать кириллицу.')
