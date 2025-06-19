import re

from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from rest_framework import serializers

from .constants import MAX_FIRST_LAST_NAME_LENGTH, MIN_SCORE, MAX_SCORE


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
    User = get_user_model()
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
    """Проверяет, что длина имени/фамилии не превышает допустимое значение."""
    if len(value) > MAX_FIRST_LAST_NAME_LENGTH:
        raise serializers.ValidationError(
            f'Длина {field_name} не должна превышать'
            ' {MAX_FIRST_LAST_NAME_LENGTH} символов'
        )
    return value


def get_score_validators():
    return [MinValueValidator(MIN_SCORE), MaxValueValidator(MAX_SCORE)]
