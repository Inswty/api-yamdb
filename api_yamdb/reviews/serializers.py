from django.contrib.auth import get_user_model
from django.utils.crypto import get_random_string
from rest_framework import serializers

from .confirmations import check_confirmation_code, send_confirmation_code
from .validators import (validate_name_length,
                         validate_user_exists,
                         validate_username_format)

User = get_user_model()


class SignUpSerializer(serializers.ModelSerializer):
    """Сериализатор для регистрации пользователей."""
    email = serializers.EmailField(max_length=254)
    username = serializers.CharField(max_length=150)

    class Meta:
        model = User
        fields = ('email', 'username')

    def validate_username(self, value):
        """Проверяет формат username и запрещенные значения."""
        return validate_username_format(value)

    def validate(self, data):
        """Проверяет существование пользователя и уникальность полей."""
        username = data.get('username')
        email = data.get('email')

        user = validate_user_exists(username, email)
        if user:
            send_confirmation_code(user)
            self.instance = user
            return data

        return data

    def create(self, validated_data):
        """Создает нового пользователя и отправляет код подтверждения."""
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=get_random_string(length=12)
        )
        send_confirmation_code(user)
        return user

    def update(self, instance, validated_data):
        """Обновляет существующего пользователя."""
        return instance


class TokenSerializer(serializers.Serializer):
    """Сериализатор для получения токена."""
    username = serializers.CharField()
    confirmation_code = serializers.CharField()

    def validate(self, data):
        """Проверяем код подтверждения."""
        username = data.get('username')
        confirmation_code = data.get('confirmation_code')

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise serializers.ValidationError(
                'Пользователь с таким username не найден'
            )

        if not check_confirmation_code(user, confirmation_code):
            raise serializers.ValidationError(
                'Неверный код подтверждения'
            )

        return data


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для работы с пользователями."""
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField(max_length=254)
    first_name = serializers.CharField(max_length=150, required=False)
    last_name = serializers.CharField(max_length=150, required=False)

    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name',
            'last_name', 'bio', 'role'
        )

    def validate_username(self, value):
        """Проверяет формат username и запрещенные значения."""
        return validate_username_format(value)

    def validate(self, data):
        """Проверяет существование пользователя и уникальность полей."""
        username = data.get('username')
        email = data.get('email')

        user = validate_user_exists(username, email)
        if user:
            self.instance = user

        return data

    def create(self, validated_data):
        """Создает нового пользователя."""
        return User.objects.create_user(**validated_data)

    def validate_first_name(self, value):
        """Проверяет, что длина имени не превышает 150 символов."""
        return validate_name_length(value, 'имени')

    def validate_last_name(self, value):
        """Проверяет, что длина фамилии не превышает 150 символов."""
        return validate_name_length(value, 'фамилии')
