import re

from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


def validate_username_format(value):
    """Проверяет формат username и запрещенные значения."""
    if value == 'me':
        raise serializers.ValidationError(
            'Использовать имя "me" в качестве username запрещено'
        )
    if not re.match(r'^[\w.@+-]+\Z', value):
        raise serializers.ValidationError(
            'Имя пользователя может содержать только буквы, '
            'цифры и символы @/./+/-/_'
        )
    return value


def validate_user_exists(username, email):
    """Проверяет существование пользователя и уникальность полей."""
    user = User.objects.filter(username=username).first()
    if user:
        if user.email != email:
            raise serializers.ValidationError(
                'Пользователь с таким username уже существует с другим email'
            )
        return user
    else:
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError(
                'Пользователь с таким email уже существует'
            )
        return None


def validate_name_length(value, field_name):
    """Проверяет, что длина имени/фамилии не превышает 150 символов."""
    if len(value) > 150:
        raise serializers.ValidationError(
            f'Длина {field_name} не должна превышать 150 символов'
        )
    return value 