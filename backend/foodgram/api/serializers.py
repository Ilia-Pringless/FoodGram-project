from django.shortcuts import get_object_or_404
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from recipes.models import (Favorite, Ingredient, IngredientsAmount, Recipe,
                            ShoppingCart, Tag)
from users.models import User
from users.serializers import UserViewSerializer


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeIngredientGETSerializer(serializers.ModelSerializer):

    id = serializers.IntegerField(source='ingredients.id')
    name = serializers.CharField(source='ingredients.name')
    measurement_unit = serializers.CharField(
        source='ingredients.measurement_unit')

    class Meta:
        model = IngredientsAmount
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeIngredientPOSTSerializer(serializers.ModelSerializer):

    class Meta:
        model = IngredientsAmount
        fields = ('id', 'amount')
        extra_kwargs = {
            'id': {'read_only': False,
                   'error_messages': {
                       'does_not_exist': 'Ингредиента не существует!'}},
            'amount': {'error_messages': {
                       'min_value': 'Слишком малое количество ингредиента!'}}
        }


class RecipeGETSerializer(serializers.ModelSerializer):
    """Сериализатор для получения рецепта"""

    tags = TagSerializer(many=True)
    author = UserViewSerializer()
    ingredients = RecipeIngredientGETSerializer(many=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients',
                  'is_favorited', 'is_in_shopping_cart',
                  'name', 'image', 'text', 'cooking_time')

    def get_is_favorited(self, obj):
        """Получение поля is_favorited"""
        request = self.context.get('request')
        user = request.user
        if user.is_anonymous:
            return False
        return (Favorite.objects.filter(
            user=user, recipe=obj).exists())

    def get_is_in_shopping_cart(self, obj):
        """Получение поля is_in_shopping_cart"""
        request = self.context.get('request')
        user = request.user
        if user.is_anonymous:
            return False
        return (ShoppingCart.objects.filter(
            user=user, recipe=obj).exists())


class RecipePOSTSerializer(serializers.ModelSerializer):
    """Сериализатор для создания рецепта"""

    ingredients = RecipeIngredientPOSTSerializer(many=True)
    tags = serializers.ListField(child=serializers.SlugRelatedField(
        slug_field='id',
        queryset=Tag.objects.all()))
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('ingredients', 'tags', 'image',
                  'name', 'text', 'cooking_time')
        extra_kwargs = {
            'cooking_time': {
                'error_messages': {
                    'min_value': 'Слишком малое время приготовления!'}}
        }

    def validate(self, attrs):
        """Валидация создания рецепта"""

        ingredients = attrs['ingredients']
        if len(attrs['ingredients']) == 0:
            raise serializers.ValidationError(
                {'ingredients': 'Необходимо указать ингредиенты!'})

        for ingredient in ingredients:
            if int(ingredient.get('amount')) <= 0:
                raise serializers.ValidationError(
                    {'amount': 'Количество должно быть больше нуля!'})

        id_ingredients = []
        for ingredient in ingredients:
            id_ingredients.append(ingredient['id'])
        if len(id_ingredients) > len(set(id_ingredients)):
            raise serializers.ValidationError(
                'Ингредиенты в рецепте не могут повторяться!')

        if attrs['cooking_time'] == 0:
            raise serializers.ValidationError(
                {'cooking_time': 'Слишком малое время приготовления!'})

        if len(attrs['tags']) == 0:
            raise serializers.ValidationError(
                {'tags': 'Необходимо указать теги!'})

        return attrs

    def add_ingredients_tags_fields(self, instance, validated_data):
        """Добавить ингредиенты и теги в рецепт"""

        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')

        for ingredient in ingredients:
            count_of_ingredient, _ = IngredientsAmount.objects.get_or_create(
                ingredients=get_object_or_404(Ingredient, pk=ingredient['id']),
                amount=ingredient['amount'])
            instance.ingredients.add(count_of_ingredient)

        for tag in tags:
            instance.tags.add(tag)
        return instance

    def create(self, validated_data):
        """Создание рецепта"""

        other_fields = {}
        other_fields['ingredients'] = validated_data.pop('ingredients')
        other_fields['tags'] = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        return self.add_ingredients_tags_fields(recipe, other_fields)

    def update(self, instance, validated_data):
        instance.ingredients.clear()
        instance.tags.clear()
        instance = self.add_ingredients_tags_fields(instance, validated_data)
        return super().update(instance, validated_data)


class FavoriteSerializer(serializers.ModelSerializer):
    """Сериализатор списка избранного"""
    recipe = serializers.PrimaryKeyRelatedField(
        queryset=Recipe.objects.all()
    )
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all()
    )

    class Meta:
        model = Favorite
        fields = ('id', 'recipe', 'user')
        validators = [
            UniqueTogetherValidator(
                queryset=Favorite.objects.all(),
                fields=('user', 'recipe'),
                message='Рецепт уже есть в избранных!',
            )
        ]
