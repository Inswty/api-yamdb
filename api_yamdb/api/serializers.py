from datetime import datetime

from django.contrib.auth import get_user_model
from django.utils.crypto import get_random_string
from rest_framework import serializers

from .confirmations import check_confirmation_code, send_confirmation_code
from reviews.constants import (
    MAX_USERNAME_LENGTH, MAX_EMAIL_LENGTH, MAX_FIRST_LAST_NAME_LENGTH,
    PASSWORD_LENGTH
)
from reviews.models import Category, Comment, Genre, Title, Review
from reviews.validators import (validate_name_length,
                                validate_user_exists,
                                validate_username_format)

User = get_user_model()


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('name', 'slug')
        model = Category


class GenreSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('name', 'slug')
        model = Genre


class TitleSerializer(serializers.ModelSerializer):
    rating = serializers.FloatField(read_only=True)
    # Для записи
    genre = serializers.SlugRelatedField(
        many=True,
        slug_field='slug',
        queryset=Genre.objects.all(),
        required=True
    )
    category = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Category.objects.all(),
        required=True
    )
    # Для чтения
    genre_read = GenreSerializer(source='genre', many=True, read_only=True)
    category_read = CategorySerializer(source='category', read_only=True)

    class Meta:
        model = Title
        fields = [
            'id', 'name', 'year', 'description', 'rating',
            'genre', 'category',          # Для записи
            'genre_read', 'category_read'    # При чтении
        ]

    def validate(self, data):
        if 'year' in data and data['year'] > datetime.now().year:
            raise serializers.ValidationError({
                'year': 'Год не может быть больше текущего.'
            })
        return data

    def validate_genre(self, value):
        if not value:
            raise serializers.ValidationError(
                'Нужно указать хотя бы один жанр'
            )
        return value

    def to_representation(self, instance):
        """Переименовываем поля для ответа"""
        data = super().to_representation(instance)
        if 'genre_read' in data:
            data['genre'] = data.pop('genre_read')
        if 'category_read' in data:
            data['category'] = data.pop('category_read')
        return data


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )
    title = serializers.SlugRelatedField(
        slug_field='id',
        read_only=True
    )

    class Meta:
        fields = '__all__'
        model = Review
        read_only_fields = ('author', 'title', 'pub_date')

    def validate(self, data):
        if self.context['request'].method == 'POST':
            title = self.context['view'].kwargs.get('title_id')
            author = self.context['request'].user
            if Review.objects.filter(title=title, author=author).exists():
                raise serializers.ValidationError(
                    'Вы уже оставляли отзыв на это произведение'
                )
        return data


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )
    review = serializers.SlugRelatedField(
        slug_field='id',
        read_only=True
    )

    class Meta:
        model = Comment
        fields = '__all__'
        read_only_fields = ('author', 'review', 'pub_date')


class SignUpSerializer(serializers.ModelSerializer):
    """Сериализатор для регистрации пользователей."""
    email = serializers.EmailField(max_length=MAX_EMAIL_LENGTH)
    username = serializers.CharField(max_length=MAX_USERNAME_LENGTH)

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
            password=get_random_string(length=PASSWORD_LENGTH)
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
    username = serializers.CharField(max_length=MAX_USERNAME_LENGTH)
    email = serializers.EmailField(max_length=MAX_EMAIL_LENGTH)
    first_name = serializers.CharField(
        max_length=MAX_FIRST_LAST_NAME_LENGTH, required=False,
        allow_blank=True, allow_null=True, default=None
    )
    last_name = serializers.CharField(
        max_length=MAX_FIRST_LAST_NAME_LENGTH, required=False,
        allow_blank=True, allow_null=True, default=None
    )

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
