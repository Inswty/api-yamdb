from django_filters.rest_framework import FilterSet, CharFilter

from reviews.models import Title


class TitleFilter(FilterSet):
    """Кастомный фильтр для модели Title."""
    category = CharFilter(field_name='category__slug')
    genre = CharFilter(field_name='genre__slug')
    name = CharFilter(field_name='name')

    class Meta:
        model = Title
        fields = ('genre', 'category', 'name', 'year')
