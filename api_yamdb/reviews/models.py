from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.contrib.auth import get_user_model

MAX_STR_LENGTH = 20
MAX_CHAR_LENGTH = 256

User = get_user_model()


class Category(models.Model):
    name = models.CharField('Категория', max_length=MAX_CHAR_LENGTH)
    slug = models.SlugField('Слаг', unique=True)

    class Meta():
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'
        default_related_name = 'titles'

    def __str__(self):
        return self.name[:MAX_STR_LENGTH]


class Genre(models.Model):
    name = models.CharField('Жанр', max_length=MAX_CHAR_LENGTH)
    slug = models.SlugField('Слаг', unique=True)

    class Meta():
        verbose_name = 'жанр'
        verbose_name_plural = 'Жанры'
        default_related_name = 'titles'

    def __str__(self):
        return self.name[:MAX_STR_LENGTH]


class Title(models.Model):
    name = models.CharField('Название', max_length=MAX_CHAR_LENGTH)
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='titles',
        verbose_name='Категория'
    )
    genres = models.ManyToManyField(
        Genre, related_name='titles',
        verbose_name='Жанры'
    )
    rating = models.IntegerField(
        'Рейтинг', null=True, blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(10)]
    )

    class Meta():
        verbose_name = 'произведение'
        verbose_name_plural = 'Произведения'
        default_related_name = 'titles'

    def __str__(self):
        return self.name[:MAX_STR_LENGTH]


class Review(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='reviews'
    )
    title = models.ForeignKey(
        Title, on_delete=models.CASCADE,
        related_name='reviews'
    )
    text = models.TextField('Текст отзыва')
    score = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)]
    )
    pub_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'отзыв'
        verbose_name_plural = 'Отзывы'
        ordering = ['-pub_date']
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'title'],
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
        ordering = ['-pub_date']
        default_related_name = 'comments'

    def __str__(self):
        return self.text[:MAX_STR_LENGTH]
