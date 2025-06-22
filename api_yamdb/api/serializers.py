from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.shortcuts import get_object_or_404
from django.utils.crypto import get_random_string
from rest_framework import serializers

from .confirmations import send_confirmation_code
from reviews.constants import PASSWORD_LENGTH
from reviews.models import Category, Comment, Genre, Title, Review
from reviews.validators import validate_username_format

User = get_user_model()


class UsernameValidationMixin:
    """Миксин для валидации username."""

    def validate_username(self, username):
        return validate_username_format(username)


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('name', 'slug')
        model = Category


class GenreSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('name', 'slug')
        model = Genre


class TitleReadSerializer(serializers.ModelSerializer):
    rating = serializers.IntegerField(read_only=True)
    genre = GenreSerializer(many=True, read_only=True)
    category = CategorySerializer(read_only=True)

    class Meta:
        model = Title
        fields = (
            'id', 'name', 'year', 'description', 'rating',
            'genre', 'category'
        )


class TitleWriteSerializer(serializers.ModelSerializer):
    rating = serializers.IntegerField(read_only=True)
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

    class Meta:
        model = Title
        fields = (
            'id', 'name', 'year', 'description', 'rating',
            'genre', 'category'
        )

    def validate_genre(self, value):
        if not value:
            raise serializers.ValidationError(
                'Нужно указать хотя бы один жанр'
            )
        return value

    def to_representation(self, instance):
        return TitleReadSerializer(instance, context=self.context).data


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )

    class Meta:
        fields = ('id', 'title', 'text', 'author', 'score', 'pub_date')
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

    class Meta:
        model = Comment
        fields = ('id', 'review', 'text', 'author', 'pub_date')
        read_only_fields = ('author', 'review', 'pub_date')


class SignUpSerializer(serializers.Serializer, UsernameValidationMixin):
    """Сериализатор для регистрации пользователей."""

    email = serializers.EmailField(
        max_length=User._meta.get_field('email').max_length)
    username = serializers.CharField(
        max_length=User._meta.get_field('username').max_length
    )

    def validate(self, data):
        """Проверяет существование пользователя и уникальность полей."""
        username = data.get('username')
        email = data.get('email')

        user = User.objects.filter(username=username, email=email).first()

        if User.objects.filter(username=username).exists() and not user:
            raise serializers.ValidationError(
                'Пользователь с таким username уже существует с другим email'
            )

        if User.objects.filter(email=email).exists() and not user:
            raise serializers.ValidationError(
                'Пользователь с таким email уже существует'
            )

        if user:
            send_confirmation_code(user)
            self.instance = user

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

        user = get_object_or_404(User, username=username)

        if not default_token_generator.check_token(user, confirmation_code):
            raise serializers.ValidationError(
                'Неверный код подтверждения'
            )

        return data


class UserSerializer(serializers.ModelSerializer, UsernameValidationMixin):
    """Сериализатор для работы с пользователями."""

    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name',
            'last_name', 'bio', 'role'
        )


class UserMeSerializer(UserSerializer):
    """Сериализатор для работы с собственным профилем пользователя."""

    role = serializers.CharField(read_only=True)
