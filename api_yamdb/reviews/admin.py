from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import Category, Comment, Genre, Title, Review, User


@admin.register(User)
class ExtendedUserAdmin(BaseUserAdmin):
    list_display = (
        'username',
        'email',
        'first_name',
        'last_name',
        'role',
        'is_staff',
    )
    list_editable = ('role',)
    list_filter = ('role', 'is_staff', 'is_superuser')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('username',)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'slug',
    )
    list_filter = ('name',)
    search_fields = ('name',)


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'slug',
    )
    list_filter = ('name',)
    search_fields = ('name',)


@admin.register(Title)
class TitleAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'year',
        'description',
        'category',
        'display_genres',
    )
    list_filter = ('name', 'genre', 'category')
    search_fields = ('name', 'year', 'genre__name', 'category__name')
    filter_horizontal = ('genre',)

    def display_genres(self, obj):
        """Это вернет список жанров через запятую."""
        return ", ".join([genre.name for genre in obj.genre.all()])

    display_genres.short_description = 'Жанры'


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = (
        'author',
        'title',
        'text',
        'score',
        'pub_date',
    )
    list_filter = ('author',)
    search_fields = ('author',)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = (
        'author',
        'review',
        'text',
        'pub_date',
    )
    list_filter = ('author',)
    search_fields = ('author',)
