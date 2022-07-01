from django.contrib import admin
from django.db.models import Count, Sum

from foodgram.settings import EMPTY_VALUE_DISPLAY
from .models import Ingredient, IngredientsAmount, Recipe, ShoppingCart, Tag


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'color', 'slug')
    list_editable = ('color', 'slug', 'name')
    search_fields = ('name',)
    list_filter = ('name',)
    empty_value_display = EMPTY_VALUE_DISPLAY


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'measurement_unit')
    list_editable = ('name', 'measurement_unit')
    search_fields = ('name',)
    list_filter = ('name',)
    empty_value_display = EMPTY_VALUE_DISPLAY


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('author',
                    'name', 'image', 'text', 'cooking_time')
    search_fields = ('name',)
    list_filter = ('name',)
    empty_value_display = EMPTY_VALUE_DISPLAY


@admin.register(IngredientsAmount)
class IngredientsAmountAdmin(admin.ModelAdmin):
    list_display = ('pk', 'ingredients', 'amount')
    list_editable = ('ingredients', 'amount')
    search_fields = ('ingredients',)
    list_filter = ('ingredients',)
    empty_value_display = EMPTY_VALUE_DISPLAY


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('user', 'count_ingredients',)
    readonly_fields = ('count_ingredients',)
    empty_value_display = EMPTY_VALUE_DISPLAY

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'

    @admin.display(description='Количество ингредиентов')
    def count_ingredients(self, obj):
        return (
            obj.recipe.all().annotate(count_ingredients=Count('ingredients'))
            .aggregate(total=Sum('count_ingredients'))['total'])
