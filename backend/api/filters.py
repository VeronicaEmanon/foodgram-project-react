from django_filters.rest_framework import (AllValuesMultipleFilter, FilterSet,
                                           filters)

from recipes.models import Ingredients, Recipe


class IngredientFilter(FilterSet):
    name = filters.CharFilter(lookup_expr="startswith")

    class Meta:
        model = Ingredients
        fields = ["name"]


class RecipeFilter(FilterSet):
    tags = AllValuesMultipleFilter(field_name="tags__slug")

    is_favourites = filters.BooleanFilter(method="filter_is_favorite")
    in_shopping_cart = filters.BooleanFilter(
        method="filter_is_in_shopping_cart"
    )

    class Meta:
        model = Recipe
        fields = ("tags", "author")

    def filter_favourites(self, queryset, name, value):
        user = self.request.user
        if value and not user.is_anonymous:
            return queryset.filter(favourites__user=user)
        return queryset
    
    def filter_in_shopping_cart(self, queryset, name, value):
        user = self.request.user
        if value and not user.is_anonymous:
            return queryset.filter(shopping_cart_user__user=user)
        return queryset
