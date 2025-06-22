import re

from django.core.exceptions import ValidationError
from rest_framework import serializers


def validate_username_format(value):
    """Проверяет формат username и запрещенные значения."""
    # Находим запрещенные символы
    allowed_pattern = r'[\w.@+-]'
    forbidden_chars = re.sub(allowed_pattern, '', value)

    if forbidden_chars:
        raise ValidationError(
            f'Имя пользователя не должно содержать символы: {forbidden_chars}'
        )

    if value.lower() == 'me':
        raise ValidationError(
            'Использовать имя "me" в качестве username запрещено'
        )
    return value
