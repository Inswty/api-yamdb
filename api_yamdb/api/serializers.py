from django.contrib.auth import get_user_model
from django.utils.crypto import get_random_string
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
import re

from .utils import check_confirmation_code, send_confirmation_code

User = get_user_model()


class SignUpSerializer(serializers.ModelSerializer):
    """Сериализатор для регистрации пользователей."""
    email = serializers.EmailField(max_length=254)
    username = serializers.CharField(max_length=150)

    class Meta:
        model = User
        fields = ('email', 'username')

    def validate_username(self, value):
        """Проверяет, что username не 'me' и соответствует формату."""
        if value == 'me':
            raise serializers.ValidationError(
                'Использовать имя "me" в качестве username запрещено'
            )
        if not re.match(r'^[\w.@+-]+\Z', value):
            raise serializers.ValidationError(
                'Имя пользователя может содержать только буквы, цифры и символы @/./+/-/_'
            )
        return value

    def validate(self, data):
        """Проверяет существование пользователя и уникальность полей."""
        username = data.get('username')
        email = data.get('email')
        try:
            user = User.objects.get(username=username, email=email)
            # Если пользователь существует, отправляем новый код
            send_confirmation_code(user)
            # Сохраняем пользователя как instance, чтобы не создавать нового
            self.instance = user
            return data
        except User.DoesNotExist:
            # Если пользователь не существует, проверяем уникальность полей
            if User.objects.filter(username=username).exists():
                raise serializers.ValidationError(
                    'Пользователь с таким username уже существует.'
                )
            if User.objects.filter(email=email).exists():
                raise serializers.ValidationError(
                    'Пользователь с таким email уже существует.'
                )
            return data

    def create(self, validated_data):
        """Создает нового пользователя и отправляет код подтверждения."""
        if self.instance is not None:
            return self.instance
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=get_random_string(length=12)
        )
        send_confirmation_code(user)
        return user


class TokenSerializer(serializers.Serializer):
    """Сериализатор для получения токена."""
    username = serializers.CharField()
    confirmation_code = serializers.CharField()

    def validate(self, data):
        """Проверяем код подтверждения."""
        username = data.get('username')
        confirmation_code = data.get('confirmation_code')
        
        user = User.objects.get(username=username)
        if not check_confirmation_code(user, confirmation_code):
            raise serializers.ValidationError(
                'Неверный код подтверждения'
            )
        
        return data


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для работы с пользователями."""
    username = serializers.CharField(
        max_length=150,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    email = serializers.EmailField(
        max_length=254,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    first_name = serializers.CharField(max_length=150, required=False)
    last_name = serializers.CharField(max_length=150, required=False)

    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name',
            'last_name', 'bio', 'role'
        )

    def validate_username(self, value):
        """Проверяет, что username не 'me'."""
        if value == 'me':
            raise serializers.ValidationError(
                'Использовать имя "me" в качестве username запрещено'
            )
        if not re.match(r'^[\w.@+-]+\Z', value):
            raise serializers.ValidationError(
                'Имя пользователя может содержать только буквы, цифры и символы @/./+/-/_'
            )
        return value

    def validate_email(self, value):
        """Проверяет, что email не 'me'."""
        if value == 'me':
            raise serializers.ValidationError(
                'Использовать имя "me" в качестве email запрещено'
            )
        return value

    def validate(self, data):
        """Проверяем существование пользователя."""
        username = data.get('username')
        email = data.get('email')
        
        # Проверяем существование пользователя
        user = User.objects.filter(username=username).first()
        if user:
            if user.email != email:
                raise serializers.ValidationError(
                    'Пользователь с таким username уже существует'
                )
            # Если email совпадает, не выдаём ошибку
            self.instance = user
        return data

    def create(self, validated_data):
        """Создаем пользователя."""
        user = User.objects.create_user(**validated_data)
        return user

    def validate_first_name(self, value):
        """Проверяет, что длина имени не превышает 150 символов."""
        if len(value) > 150:
            raise serializers.ValidationError(
                'Длина имени не должна превышать 150 символов'
            )
        return value

    def validate_last_name(self, value):
        """Проверяет, что длина фамилии не превышает 150 символов."""
        if len(value) > 150:
            raise serializers.ValidationError(
                'Длина фамилии не должна превышать 150 символов'
            )
        return value 