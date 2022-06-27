import django_filters as filters
from recipes.models import Ingredient, Recipe, Tag

from users.models import User


class IngredientNameFilter(filters.FilterSet):
    """Фильтрация ингредиентов"""
    name = filters.CharFilter(field_name='name', lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ('name',)


class RecipeFilter(filters.FilterSet):
    """Фильтрация рецептов"""
    IN = 1
    OUT = 0
    CHOICES = (
        (IN, 1),
        (OUT, 0),
    )
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        queryset=Tag.objects.all(),
        to_field_name='slug'
    )
    author = filters.ModelChoiceFilter(
        queryset=User.objects.all()
    )
    is_favorited = filters.ChoiceFilter(
        method='get_is_favorited',
        choices=CHOICES
    )
    is_in_shopping_cart = filters.ChoiceFilter(
        method='get_is_in_shopping_cart',
        choices=CHOICES
    )

    class Meta:
        model = Recipe
        fields = ('tags', 'author')

    def get_is_favorited(self, queryset, name, value):
        user = self.request.user
        if value and not user.is_anonymous:
            return queryset.filter(favorites__user=user)
        return queryset

    def get_is_in_shopping_cart(self, queryset, name, value):
        user = self.request.user
        if value and not user.is_anonymous:
            return queryset.filter(purchase__user=user)
        return queryset
