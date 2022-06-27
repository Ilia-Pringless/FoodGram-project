from recipes.models import Recipe
from rest_framework.serializers import ModelSerializer


class ShortRecipeSerializer(ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time',)
