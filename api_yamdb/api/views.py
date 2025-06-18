from django.contrib.auth import get_user_model
from django_filters.rest_framework import (
    DjangoFilterBackend, FilterSet, CharFilter
)
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets, filters
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView

from .confirmations import check_confirmation_code
from .permissions import (
    IsAdmin, IsAdminOrReadOnly, IsAuthenticatedOrReadOnly, 
    IsAuthorModeratorAdminOrReadOnly
)
from .serializers import (
    CategorySerializer, CommentSerializer, GenreSerializer, ReviewSerializer,
    TitleSerializer, SignUpSerializer, TokenSerializer, UserSerializer
)
from reviews.models import Category, Comment, Genre, Title, Review, User

User = get_user_model()


class TitleFilter(FilterSet):
    """Кастомный фильтр для модели Title."""
    genre = CharFilter(field_name='genre__slug', lookup_expr='exact')
    category = CharFilter(field_name='category__slug', lookup_expr='exact')

    class Meta:
        model = Title
        fields = ('genre', 'category', 'name', 'year')


class TitleViewSet(viewsets.ModelViewSet):
    queryset = (
        Title.objects.select_related('category').prefetch_related('genre')
    )
    serializer_class = TitleSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter
    ordering_fields = ('name', 'year', 'rating')
    permission_classes = (IsAdminOrReadOnly,)


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = 'slug'
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    filterset_fields = ('name',)
    search_fields = ('name',)
    ordering_fields = ('name',)
    permission_classes = (IsAdminOrReadOnly,)


class GenreViewSet(viewsets.ModelViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    lookup_field = 'slug'
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    filterset_fields = ('name',)
    search_fields = ('name',)
    ordering_fields = ('name',)
    permission_classes = (IsAdminOrReadOnly,)


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    http_method_names = ('get', 'post', 'patch', 'delete')
    permission_classes = (IsAuthenticatedOrReadOnly, IsAuthorModeratorAdminOrReadOnly)

    def perform_create(self, serializer):
        title_id = self.kwargs.get('title_id')
        title = get_object_or_404(Title, id=title_id)
        serializer.save(author=self.request.user, title=title)


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, IsAuthorModeratorAdminOrReadOnly)


class SignUpView(APIView):
    """Регистрация нового пользователя."""
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = SignUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class TokenView(APIView):
    """View для получения токена."""
    permission_classes = (AllowAny,)

    def post(self, request):
        username = request.data.get('username')
        if not username:
            serializer = TokenSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(serializer.errors,
                                status=status.HTTP_400_BAD_REQUEST)
        else:
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                return Response(
                    {'detail': 'Пользователь не найден'},
                    status=status.HTTP_404_NOT_FOUND
                )
        serializer = TokenSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)
        user = User.objects.get(
            username=serializer.validated_data['username'])
        if not check_confirmation_code(
            user, serializer.validated_data['confirmation_code']
        ):
            return Response(
                {'detail': 'Неверный код подтверждения'},
                status=status.HTTP_400_BAD_REQUEST
            )
        refresh = RefreshToken.for_user(user)
        return Response({
            'token': str(refresh.access_token),
        })


class UserViewSet(viewsets.ModelViewSet):
    """ViewSet для работы с пользователями."""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'username'
    filter_backends = [SearchFilter]
    search_fields = ['username', 'email']
    permission_classes = (IsAdmin,)
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_permissions(self):
        if self.action == 'me':
            return (IsAuthenticated(),)
        return super().get_permissions()

    def get_queryset(self):
        if self.action == 'me':
            return User.objects.filter(id=self.request.user.id)
        return super().get_queryset()

    @action(
        methods=['get', 'patch'],
        detail=False,
        url_path='me',
        url_name='me',
        permission_classes=[IsAuthenticated]
    )
    def me(self, request):
        serializer = self.get_serializer(request.user)
        if request.method == 'PATCH':
            data = request.data.copy()
            data.pop('role', None)  # Удаляем поле role, если есть.
            serializer = self.get_serializer(
                request.user,
                data=data,
                partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
        return Response(serializer.data)
