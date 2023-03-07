from django.db.models import Exists, F, OuterRef, Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, status
from rest_framework.decorators import action
from rest_framework.permissions import SAFE_METHODS
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from recipes.models import (Favourite, IngredientInRecipe, Ingredients, Recipe,
                            ShoppingCart, Tags)

from .filters import IngredientFilter, RecipeFilter
from .permissions import IsAuthorOrReadOnly
from .serializers import (FavouritesSerializer, IngredientsSerializer,
                          RecipePOSTUPDELSerializer, RecipeREADSerializer, 
                          ShoppingCartSerializer, TagsSerializer)


class IngredientsViewSet(ModelViewSet):
    queryset = Ingredients.objects.all()
    serializer_class = IngredientsSerializer
    pagination_class = None
    permission_classes = (permissions.AllowAny, )
    filter_backends = (DjangoFilterBackend, )
    filterset_class = IngredientFilter
    search_fields = ('^name',)


class TagsViewsSet(ModelViewSet):
    queryset = Tags.objects.all()
    serializer_class = TagsSerializer
    pagination_class = None
    # permission_classes = (permissions.IsAuthenticatedOrReadOnly,)



class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipePOSTUPDELSerializer
    permission_classes = (IsAuthorOrReadOnly, )
    filter_backends = (DjangoFilterBackend, )
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS == "GET":
            RecipeREADSerializer
        return RecipePOSTUPDELSerializer
    
    def get_queryset(self):
        queryset = Recipe.objects.select_related(
            "author"
        ).prefetch_related("ingredients", "tags")
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
            raise Exception("Рецепт может удалить только автор")
        instance.delite()

    @action(
        methods=["POST", "DELETE"],
        detail=True,
        permission_classes=[permissions.IsAuthenticated]
    )
    def favorite(self, request, pk):
        if request.method == "POST":
            if Favourite.objects.filter(
                user=request.user, recipe__id=pk
            ).exists():
                return Response(
                    {"error": "Рецепт уже добавлен в избранное"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            recipe = get_object_or_404(Recipe, pk=pk)
            instance = Favourite.objects.create(
                user=request.user,
                recipe=recipe
            )
            serializer = FavouritesSerializer(instance)
            return Response(
                data=serializer.data,
                status=status.HTTP_201_CREATED
            )
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
            recipe = get_object_or_404(Recipe, pk=pk)
            instance = ShoppingCart.objects.create(
                user=request.user,
                recipe=recipe
            )
            serializer = ShoppingCartSerializer(instance)
            return Response(
                data=serializer.data,
                status=status.HTTP_201_CREATED
            )
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
        items = IngredientInRecipe.objects.select_related(
            "recipe", "ingredient"
        )

        if request.user.is_authenticated:
            items = items.filter(
                recipe__shopping_cart__user=request.user
            )
        else:
            items = items.filter(
                recipe_id__in=request.session["purchases"]
            )
        items = items.values(
            "ingredient__name", "ingredient__measurement_unit"
        ).annotate(
            name=F("ingredient__name"),
            units=F("ingredient__measurement_unit"),
            total=Sum("amount"),
        ).order_by("-total")

        text = "\n".join([
            f"{item['name']}({item['units']}) - {item['total']}"
            for item in items
        ])

        filename = "foodgram_shopping_cart.txt"
        response = HttpResponse(text, content_type="text/plain")
        response["Content=Disposition"] = f"attachment; {filename}"
        return response