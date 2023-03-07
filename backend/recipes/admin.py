from django.contrib import admin

from .models import (Favourite, IngredientInRecipe, Ingredients, Recipe,
                     ShoppingCart, Tags)


class RecipeIngredientInline(admin.TabularInline):
    model = IngredientInRecipe
    min_num = 1
    extra = 0

class RecipeAdmin(admin.ModelAdmin):
    def added_to_favorites_amount(self, obj):
        return Favourite.objects.filter(recipe=obj).count()
    added_to_favorites_amount.short_description = "Добавлений в избранное"

    
    list_display = ("pk", "author", "image", "name", "pub_date", "cooking_time", "text", "added_to_favorites_amount")
    list_filter = ("name", "author", )
    search_fields = ("name", )
    filter_horizontal = ("tags", )
    autocomplete_fields = ("ingredients", )
    inlines = (RecipeIngredientInline, )
    readonly_fields = ("added_to_favorites_amount", )
    empty_value_display = "-пусто-"

    def save_model(self, request, obj, form, change):
        obj.save(from_admin=True)


class TagsAdmin(admin.ModelAdmin):
    list_display = ("name", "color", "slug", )
    empty_value_display = "-пусто-"


class IngredientsAdmin(admin.ModelAdmin):
    list_display = ("name", "measurement_unit", )
    search_fields = ("name", )
    empty_value_display = "-пусто-"


class IngredientsInRecipeAdmin(admin.ModelAdmin):
    list_display = ("recipe", "ingredient", "amount")
    empty_value_display = "-пусто-"

class FavouriteAdmin(admin.ModelAdmin):
    list_display = ("user", "recipe", )
    empty_value_display = "-пусто-"


class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ("user", )
    empty_value_display = "-пусто-"


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredients, IngredientsAdmin)
admin.site.register(Tags, TagsAdmin)
admin.site.register(Favourite, FavouriteAdmin)
admin.site.register(ShoppingCart, ShoppingCartAdmin)
admin.site.register(IngredientInRecipe, IngredientsInRecipeAdmin)
