import re
from datetime import datetime

from django.core.exceptions import ValidationError


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


def current_year():
    """Функция для получения текущего года"""
    return datetime.now().year
