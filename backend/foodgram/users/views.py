from django.db import DatabaseError
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import permissions, status
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.decorators import action
from rest_framework.response import Response

from foodgram.pagination import LimitPageNumberPagination

from .models import Follow, User
from .serializers import SubscriptionSerializer, TokenCreateSerializer


class TokenView(ObtainAuthToken):
    """Создание токена"""

    def _action(self, serializer):
        if serializer.user.is_blocked:
            return Response('Аккаунт заблокирован!',
                            status=status.HTTP_400_BAD_REQUEST)
        return super()._action(serializer)

    def post(self, request, *args, **kwargs):
        serializer = TokenCreateSerializer(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        email = serializer.data.get('email')
        user = get_object_or_404(User, email=email)
        token, created = Token.objects.get_or_create(user=user)
        return Response({'auth_token': f'{token}'},
                        status=status.HTTP_200_OK)


class CustomUsersViewSet(UserViewSet):
    pagination_class = LimitPageNumberPagination
    serializer_class = SubscriptionSerializer

    def get_subscribtion_serializer(self, *args, **kwargs):
        """Добавить параметры в контекст сериализатора"""
        kwargs.setdefault('context', self.get_serializer_context())
        return SubscriptionSerializer(*args, **kwargs)

    @action(detail=False, methods=['get'])
    def subscriptions(self, request):
        """Просмотр подписок"""
        queryset = User.objects.filter(following__user=request.user)
        serializer = self.get_subscribtion_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create_subscribe(self, request, author):
        """Создание подписки"""

        if request.user == author:
            return Response('Нельзя подписаться на себя!',
                            status=status.HTTP_400_BAD_REQUEST)
        try:
            subscribe = Follow.objects.create(user=request.user, author=author)
        except DatabaseError:
            return Response('Вы уже подписаны на автора!',
                            status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_subscribtion_serializer(subscribe.author)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete_subscribe(self, request, author):
        """Удаление подписки"""
        user = request.user
        try:
            obj = Follow.objects.get(user=user, author=author)
            obj.delete()
        except Follow.DoesNotExist:
            return Response('Подписки не существует.',
                            status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['POST', 'DELETE'],
            permission_classes=[permissions.IsAuthenticated])
    def subscribe(self, request, id=None):
        try:
            author = User.objects.get(id=id)
        except User.DoesNotExist:
            return Response('Пользователь не найден.',
                            status=status.HTTP_404_NOT_FOUND)
        if request.method == 'POST':
            return self.create_subscribe(request, author=author)
        return self.delete_subscribe(request, author)
