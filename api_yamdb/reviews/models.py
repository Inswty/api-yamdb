from datetime import datetime

from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator
from django.db import models

from .constants import (
    MAX_STR_LENGTH, MAX_CHAR_LENGTH, MAX_SLUG_LENGTH,
    MAX_USERNAME_LENGTH, MAX_EMAIL_LENGTH, MAX_FIRST_LAST_NAME_LENGTH
)
from .validators import get_score_validators, validate_username_format


class User(AbstractUser):
    """Кастомная модель пользователя."""

    class Role(models.TextChoices):
        """Роли пользователей."""

        USER = 'user', 'Пользователь'
        MODERATOR = 'moderator', 'Модератор'
        ADMIN = 'admin', 'Администратор'

    username = models.CharField(
        'Имя пользователя',
        max_length=MAX_USERNAME_LENGTH,
        unique=True,
        validators=(validate_username_format,),
        help_text=(
            'Обязательное поле. Не более 150 символов. '
            'Только буквы, цифры и символы @/./+/-/_.'
        )
    )
    email = models.EmailField(
        'Email',
        unique=True,
        max_length=MAX_EMAIL_LENGTH,
    )
    first_name = models.CharField(
        'Имя',
        max_length=MAX_FIRST_LAST_NAME_LENGTH,
        blank=True, null=True
    )
    last_name = models.CharField(
        'Фамилия',
        max_length=MAX_FIRST_LAST_NAME_LENGTH,
        blank=True, null=True
    )
    bio = models.TextField(
        'Биография',
        blank=True, null=True
    )
    role = models.CharField(
        'Роль',
        max_length=max(len(role[0]) for role in Role.choices),
        choices=Role.choices,
        default=Role.USER
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    @property
    def is_admin(self):
        """Проверяет, является ли пользователь администратором.

        Суперпользователь всегда является администратором.
        """
        return self.is_superuser or self.role == self.Role.ADMIN

    @property
    def is_moderator(self):
        return self.role == self.Role.MODERATOR


class Category(models.Model):
    name = models.CharField('Категория', max_length=MAX_CHAR_LENGTH)
    slug = models.SlugField('Слаг', unique=True, max_length=MAX_SLUG_LENGTH)

    class Meta():
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'
        default_related_name = 'titles'
        ordering = ('id',)

    def __str__(self):
        return self.name[:MAX_STR_LENGTH]


class Genre(models.Model):
    name = models.CharField('Жанр', max_length=MAX_CHAR_LENGTH)
    slug = models.SlugField('Слаг', unique=True, max_length=MAX_SLUG_LENGTH)

    class Meta():
        verbose_name = 'жанр'
        verbose_name_plural = 'Жанры'
        default_related_name = 'titles'
        ordering = ('id',)

    def __str__(self):
        return self.name[:MAX_STR_LENGTH]


class Title(models.Model):
    name = models.CharField('Название', max_length=MAX_CHAR_LENGTH)
    year = models.IntegerField(
        'Год выпуска',
        validators=[MaxValueValidator(datetime.now().year)]
    )
    description = models.TextField('Описание', blank=True, null=True)
    genre = models.ManyToManyField(
        Genre, related_name='titles',
        verbose_name='Жанры'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='titles',
        verbose_name='Категория'
    )

    class Meta():
        verbose_name = 'произведение'
        verbose_name_plural = 'Произведения'
        default_related_name = 'titles'
        ordering = ('id',)

    def __str__(self):
        return self.name[:MAX_STR_LENGTH]


class Review(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='автор'
    )
    title = models.ForeignKey(
        Title, on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='произведение'
    )
    text = models.TextField('Текст отзыва')
    score = models.IntegerField(
        'оценка',
        validators=get_score_validators()
    )
    pub_date = models.DateTimeField('дата публикации', auto_now_add=True)

    class Meta:
        verbose_name = 'отзыв'
        verbose_name_plural = 'Отзывы'
        ordering = ('-pub_date',)
        constraints = [
            models.UniqueConstraint(
                fields=('author', 'title'),
                name='unique_review'
            )
        ]

    def __str__(self):
        return self.text[:MAX_STR_LENGTH]


class Comment(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор комментария'
    )
    review = models.ForeignKey(
        Review, on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Отзыв'
    )
    text = models.TextField('Текст комментария')
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)

    class Meta():
        verbose_name = 'комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ('-pub_date',)
        default_related_name = 'comments'

    def __str__(self):
        return self.text[:MAX_STR_LENGTH]
