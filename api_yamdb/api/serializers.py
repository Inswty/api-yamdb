from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.relations import SlugRelatedField


from reviews.models import Category, Comment, Genre, Title, Review

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
    # Для записи
    genre = serializers.SlugRelatedField(
        many=True,
        slug_field='slug',
        queryset=Genre.objects.all(),
        required=False
    )
    category = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Category.objects.all(),
        required=False
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

    def to_representation(self, instance):
        """Переименовываем поля для ответа"""
        data = super().to_representation(instance)
        if 'genre_read' in data:
            data['genre'] = data.pop('genre_read')
        if 'category_read' in data:
            data['category'] = data.pop('category_read')
        return data


class ReviewSerializer(serializers.ModelSerializer):
    author = SlugRelatedField(slug_field='username', read_only=True)
    title = serializers.SlugRelatedField(
        slug_field='id',
        queryset=Title.objects.all(),
        write_only=True
    )

    class Meta:
        fields = '__all__'
        model = Review


class CommentSerializer(serializers.ModelSerializer):
    author = SlugRelatedField(slug_field='username', read_only=True)
    review = serializers.SlugRelatedField(
        slug_field='id',
        queryset=Review.objects.all(),
        write_only=True
    )

    class Meta:
        fields = '__all__'
        model = Comment
