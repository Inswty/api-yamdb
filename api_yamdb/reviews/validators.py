import re

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from rest_framework import serializers

from .constants import MAX_FIRST_LAST_NAME_LENGTH


def validate_username_format(value):
    """Проверяет формат username и запрещенные значения."""
    if not re.match(r'^[\w.@+-]+\Z', value):
        raise ValidationError(
            'Имя пользователя может содержать только буквы, '
            'цифры и символы @/./+/-/_'
        )
    if value.lower() == 'me':
        raise ValidationError(
            'Использовать имя "me" в качестве username запрещено'
        )
    return value


def validate_user_exists(username, email):
    """Проверяет существование пользователя и уникальность полей."""
    user_model = get_user_model()
    user = user_model.objects.filter(username=username).first()
    if user:
        if user.email != email:
            raise serializers.ValidationError(
                'Пользователь с таким username уже существует с другим email'
            )
        return user
    else:
        if user_model.objects.filter(email=email).exists():
            raise serializers.ValidationError(
                'Пользователь с таким email уже существует'
            )
        return None


def validate_name_length(value, field_name):
    """Проверяет, что длина имени/фамилии не превышает допустимое значение."""
    if not value:
        return value
    if len(value) > MAX_FIRST_LAST_NAME_LENGTH:
        raise serializers.ValidationError(
            f'Длина {field_name} не должна превышать'
            ' {MAX_FIRST_LAST_NAME_LENGTH} символов'
        )
    return value
