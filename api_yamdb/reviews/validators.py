import re

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from rest_framework import serializers

from .constants import MIN_SCORE, MAX_SCORE


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


def get_score_validators():
    return [MinValueValidator(MIN_SCORE), MaxValueValidator(MAX_SCORE)]
