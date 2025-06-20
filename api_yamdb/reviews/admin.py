from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Category, Comment, Genre, Title, Review, User
from .forms import CustomUserCreationForm


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    
    list_display = (
        'username',
        'email',
        'first_name',
        'last_name',
        'role',
        'is_staff',
    )
    list_filter = ('role', 'is_staff', 'is_superuser')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('username',)
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'role'),
        }),
    )
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Персональная информация', {'fields': ('first_name', 'last_name', 'email', 'bio')}),
        ('Права доступа', {
            'fields': ('role', 'is_active', 'is_staff', 'is_superuser'),
        }),
        ('Важные даты', {'fields': ('last_login', 'date_joined')}),
    )


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'slug',
    )


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'slug',
    )


@admin.register(Title)
class TitleAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'year',
        'description',
        'category',
    )


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = (
        'author',
        'title',
        'text',
        'score',
        'pub_date',
    )


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = (
        'author',
        'review',
        'text',
        'pub_date',
    )
