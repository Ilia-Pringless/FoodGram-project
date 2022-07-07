from django.db import DatabaseError
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework.backends import DjangoFilterBackend
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import SAFE_METHODS, IsAuthenticated
from rest_framework.response import Response

from foodgram.pagination import LimitPageNumberPagination
from recipes.models import Favorite, Ingredient, Recipe, ShoppingCart, Tag

from .filters import IngredientNameFilter, RecipeFilter
from .nested import ShortRecipeSerializer
from .permissions import IsAdmin, IsAuthorOrAdminOrReadOnly
from .serializers import (IngredientSerializer, RecipeGETSerializer,
                          RecipePOSTSerializer, TagSerializer)


class TagViewSet(viewsets.ModelViewSet):
    """Отображение тега/списка тегов"""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAdmin,)


class IngredientViewSet(viewsets.ModelViewSet):
    """Отображение ингредиента/списка ингредиентов"""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (IsAdmin,)
    filterset_class = IngredientNameFilter
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientNameFilter


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет для работы с рецептами"""

    pagination_class = LimitPageNumberPagination
    queryset = Recipe.objects.all()
    permission_classes = (IsAuthorOrAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeGETSerializer
        return RecipePOSTSerializer

    def perform_create(self, serializer):
        """Создание рецепта"""
        serializer.save(author=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        serializer = RecipeGETSerializer(
            instance=serializer.instance,
            context={'request': self.request}
        )
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        serializer = RecipeGETSerializer(
            instance=serializer.instance,
            context={'request': self.request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create_favorite(self, request, recipe):
        """Добавление рецепта в избранное"""
        try:
            Favorite.objects.create(user=request.user, recipe=recipe)
        except DatabaseError:
            return Response('Рецепт уже в избранном',
                            status=status.HTTP_400_BAD_REQUEST)
        serializer = ShortRecipeSerializer(recipe)
        return Response(serializer.data,
                        status=status.HTTP_201_CREATED)

    def delete_favorite(self, request, recipe):
        """Удаление рецепта из избранного"""
        user = request.user
        recipe = self.get_object()
        favorite = get_object_or_404(Favorite, user=user, recipe=recipe)
        favorite.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=('post', 'delete',),
            permission_classes=(IsAuthenticated,))
    def favorite(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)
        if request.method == 'POST':
            return self.create_favorite(request, recipe)
        return self.delete_favorite(request, recipe)

    def create_shopping_cart(self, request, recipe, shopping_cart):
        """Добавление рецепта в список покупок"""
        if shopping_cart.recipe.filter(pk__in=(recipe.pk,)).exists():
            return Response('Рецепт уже в списке!',
                            status=status.HTTP_400_BAD_REQUEST)
        shopping_cart.recipe.add(recipe)
        serializer = ShortRecipeSerializer(recipe)
        return Response(serializer.data,
                        status=status.HTTP_201_CREATED)

    def delete_shopping_cart(self, request, recipe, shopping_cart):
        """Удаление рецепта из списка покупок"""
        if not shopping_cart.recipe.filter(pk__in=(recipe.pk,)).exists():
            return Response('Нечего удалять',
                            status=status.HTTP_400_BAD_REQUEST)
        shopping_cart.recipe.remove(recipe)
        return Response(
            status=status.HTTP_204_NO_CONTENT,)

    @action(detail=True, methods=('post', 'delete',),
            permission_classes=(IsAuthenticated,))
    def shopping_cart(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)
        shopping_cart = (
            ShoppingCart.objects.get_or_create(user=request.user)[0])
        if request.method == 'POST':
            return self.create_shopping_cart(request, recipe, shopping_cart)
        return self.delete_shopping_cart(request, recipe, shopping_cart)


class ShoppingCartViewSet(viewsets.GenericViewSet):
    NAME = 'ingredients__ingredients__name'
    MEASUREMENT_UNIT = 'ingredients__ingredients__measurement_unit'
    queryset = ShoppingCart.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = ShortRecipeSerializer

    def create_shopping_cart_content(self, request):
        recipes = (
            request.user.buyer.recipe.prefetch_related('ingredients')
        )
        return (recipes.order_by(self.NAME)
                .values(self.NAME, self.MEASUREMENT_UNIT)
                .annotate(total=Sum('ingredients__amount')))

    def create_ingredients_content(self, ingredients):
        content = ''
        for ingredient in ingredients:
            content += (f'{ingredient[self.NAME]}'
                        f' ({ingredient[self.MEASUREMENT_UNIT]})'
                        f' — {ingredient["total"]}\r\n')
        return content

    @action(detail=False, methods=['GET'],
            permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
        """Формирование списка покупок и его печать в файл"""
        try:
            ingredients = self.create_shopping_cart_content(request)
        except ShoppingCart.DoesNotExist:
            return Response('Список покупок пуст!',
                            status=status.HTTP_400_BAD_REQUEST)
        shop_txt = self.create_ingredients_content(ingredients)
        pdfmetrics.registerFont(
            TTFont('Arial', 'arialbi.ttf', 'UTF-8'))
        response = HttpResponse(
            shop_txt, content_type='application/pdf')
        filename = 'shopping_list.pdf'
        response['Content-Disposition'] = 'attachment; filename={0}'.format(
            filename)
        page = canvas.Canvas(response)
        page.setFont('Arial', size=24)
        page.drawString(200, 800, 'Список покупок')
        page.setFont('Arial', size=16)
        height = 750
        for i in shop_txt.split():
            page.drawString(100, height, i)
            height -= 50
        page.showPage()
        page.save()
        return response
