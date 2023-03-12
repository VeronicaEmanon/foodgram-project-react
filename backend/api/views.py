from django.db.models import Exists, F, OuterRef, Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, status
from rest_framework.decorators import action
from rest_framework.permissions import SAFE_METHODS
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from datetime import datetime

from recipes.models import (Favourite, IngredientInRecipe, Ingredients, Recipe,
                            ShoppingCart, Tags)
from .filters import IngredientFilter, RecipeFilter
from .permissions import IsAuthorOrReadOnly
from .serializers import (IngredientsSerializer, RecipePOSTUPDELSerializer,
                          RecipeListSerializer, ShoppingCartSerializer, 
                          TagsSerializer, RecipeInfoSerializer)


class IngredientsViewSet(ModelViewSet):
    queryset = Ingredients.objects.all()
    serializer_class = IngredientsSerializer
    pagination_class = None
    filter_backends = (DjangoFilterBackend, )
    filterset_class = IngredientFilter
   

class TagsViewsSet(ModelViewSet):
    queryset = Tags.objects.all()
    serializer_class = TagsSerializer
    pagination_class = None
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipePOSTUPDELSerializer
    permission_classes = (IsAuthorOrReadOnly, )
    filter_backends = (DjangoFilterBackend, )
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS == "GET":
            RecipeListSerializer
        return RecipePOSTUPDELSerializer
    
    def get_queryset(self):
        queryset = Recipe.objects.select_related(
            "author"
        ).prefetch_related(
            "ingredients",
            "tags"
        )
        user = self.request.user
        if user.is_authenticated:
            queryset = queryset.annotate(
                is_favorited=Exists(
                    Favourite.objects.filter(
                        user=user,
                        recipe=OuterRef("pk")
                    )
                ),
                is_in_shopping_cart=Exists(
                    ShoppingCart.objects.filter(
                        user=user,
                        recipe=OuterRef("pk")
                    )
                )
            )
        return queryset

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def perform_destroy(self, instance):
        if self.request.user != instance.author:
            raise Exception("Рецепт может удалить только автор или суперюзер")
        instance.delete()

    @action(
        methods=["POST", "DELETE"],
        detail=True,
        url_path='favorite',
        url_name='favorite',
        permission_classes=[permissions.IsAuthenticated]
    )
    def favorite(self, request, pk):
        if request.method == "POST":
            if Favourite.objects.filter(
                user=request.user, recipe__id=pk
            ).exists():
                return Response(
                    {"errors": "Рецепт уже добавлен"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            recipe = get_object_or_404(Recipe, id=pk)
            Favourite.objects.create(user=request.user, recipe=recipe)
            serializer = RecipeInfoSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if Favourite.objects.filter(user=request.user, recipe__id=pk).exists():
            Favourite.objects.filter(user=request.user, recipe__id=pk).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST) 

    @action(
        methods=["POST", "DELETE"],
        detail=True,
        permission_classes=[permissions.IsAuthenticated]
    )
    def shopping_cart(self, request, pk):
        if request.method == "POST":
            if ShoppingCart.objects.filter(
                user=request.user, recipe__id=pk
            ).exists():
                return Response(
                    {"error": "Рецепт уже добавлен в корзину"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            recipe = get_object_or_404(Recipe, id=pk)
            instance = ShoppingCart.objects.create(
                user=request.user,
                recipe=recipe
            )
            serializer = ShoppingCartSerializer(instance)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        if ShoppingCart.objects.filter(
            user=request.user, recipe__id=pk
        ).exists():
            ShoppingCart.objects.filter(
                user=request.user, recipe__id=pk
            ).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(
            methods=["GET"],
            detail=False,
            permission_classes=[permissions.IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        user = request.user
        if not user.shopping_cart_user.exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        ingredients = IngredientInRecipe.objects.filter(
        ).values(
            "ingredient__name",
            "ingredient__measurement_unit"
        ).annotate(amount=Sum("amount"))
        today = datetime.today()
        shopping_list = (
            f"Список покупок для: {user.get_username()}\n\n"
            f"Дата: {today:%Y-%m-%d}\n\n"
        )
        shopping_list += '\n'.join([
            f"- {ingredient['ingredient__name']}"
            f"({ingredient['ingredient__measurement_unit']})"
            f" - {ingredient['amount']}"
            for ingredient in ingredients
        ])
        filename = "foodgram_shopping_cart.txt"
        response = HttpResponse(shopping_list, content_type="text/plain")
        response["Content=Disposition"] = f"attachment; {filename}"
        return response