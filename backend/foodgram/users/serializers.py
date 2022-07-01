from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers
from rest_framework.authtoken.models import Token

from api.nested import ShortRecipeSerializer
from .models import User


class UserViewSerializer(UserSerializer):
    """Сериализатор для получения информации о пользователе"""
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed')

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        return (user.is_authenticated
                and obj.following.filter(user=user).exists())


class UserLoginSerializer(UserCreateSerializer):
    """Сериализатор регистрации пользователя"""
    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'password')


class TokenCreateSerializer(serializers.ModelSerializer):
    """Сериализатор получения токена"""
    password = serializers.CharField(
        required=True
    )
    email = serializers.EmailField(
        required=True
    )

    class Meta:
        model = Token
        fields = ('password', 'email')


class SubscriptionSerializer(UserViewSerializer):
    """Сериализатор подписки"""
    recipes = ShortRecipeSerializer(many=True)
    recipes_count = serializers.SerializerMethodField()

    class Meta(UserViewSerializer.Meta):
        fields = UserViewSerializer.Meta.fields + ('recipes', 'recipes_count',)

    def get_recipes_count(self, obj):
        return obj.recipes.count()
