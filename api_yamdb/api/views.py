from django.contrib.auth import get_user_model
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User
from .permissions import IsAdmin
from .serializers import SignUpSerializer, TokenSerializer, UserSerializer
from .utils import check_confirmation_code

User = get_user_model()


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
            data.pop('role', None)  # Удаляем поле role, если оно есть.
            serializer = self.get_serializer(
                request.user,
                data=data,
                partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
        return Response(serializer.data)
