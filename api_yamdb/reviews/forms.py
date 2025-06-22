from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError

from .models import User
from .validators import validate_username_format


class CustomUserCreationForm(UserCreationForm):
    """Форма для создания пользователей в админке."""

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email', 'role')

    def clean_username(self):
        """Проверяет формат username."""
        username = self.cleaned_data.get('username')
        if username:
            username = validate_username_format(username)
        return username

    def clean(self):
        """Проверяет уникальность username и email."""
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        email = cleaned_data.get('email')

        if username and email:
            user = User.objects.filter(username=username).first()
            if user:
                if user.email != email:
                    raise ValidationError(
                        'Пользователь с таким username уже существует с другим email'
                    )
                if not self.instance.pk:
                    raise ValidationError('Пользователь уже существует')
            elif User.objects.filter(email=email).exists():
                raise ValidationError(
                    'Пользователь с таким email уже существует'
                )
        return cleaned_data
