from rest_framework.serializers import ModelSerializer

from recipes.models import Recipe


class ShortRecipeSerializer(ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time',)
