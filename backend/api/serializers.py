import base64
from django.contrib.auth import get_user_model
import webcolors
from django.core.files.base import ContentFile
from django.db import transaction
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers

from recipes.models import (IngredientInRecipe, Ingredients, Recipe,
                            ShoppingCart, Tags, Favourite)
from users.models import Follow

User = get_user_model()


class CustomUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
        )
    
    def get_is_subscribed(self, obj):
        user = self.context.get("request").user
        if user.is_anonymous:
            return False
        return Follow.objects.filter(user=user, author=obj).exists()


class POSTUserSerializer(UserCreateSerializer):

    class Meta:
        model = User
        fields = (
            "username",
            "password",
            "email",
            "first_name",
            "last_name"
        )
    
    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data.get("username"),
            email=validated_data.get("email"),
            first_name=validated_data.get("first_name"),
            last_name=validated_data.get("last_name")
        )
        user.set_password(validated_data.get("password"))
        user.save()
        return user


class Hex2NameColor(serializers.Field):

    def to_representation(self, value):
        return value
    
    def to_internal_value(self, data):
        try:
            data = webcolors.hex_to_name(data)
        except ValueError:
            raise serializers.ValidationError("Для этого цвета нет имени")
        return data


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith("data:image"):
            format, imgstr = data.split(";base64")
            ext = format.split("/")[-1]
            data = ContentFile(base64.b64decode(imgstr), name="temp." + ext)
        return super().to_internal_value(data)


class TagsSerializer(serializers.ModelSerializer):
    color = Hex2NameColor 

    class Meta:
        model = Tags
        fields = ("id", "name", "color", "slug")

    
class IngredientsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredients
        fields = ("id", "name", "measurement_unit")


class IngredientsInRecipeSerializers(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(
        source="ingredeint.id"
    )
    name = serializers.ReadOnlyField(source="ingredient.name")
    measurement_unit = serializers.ReadOnlyField(source="ingredient.measurement_unit")

    class Meta:
        model = IngredientInRecipe
        fields = (
            "id",
            "name", 
            "amount", 
            "measurement_unit",
        )


class AmountRecipeSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredients.objects.all())
    amount = serializers.IntegerField()

    class Meta:
        model = IngredientInRecipe
        fields = ("id",  "amount")


class RecipeListSerializer(serializers.ModelSerializer):
    author = CustomUserSerializer(read_only=True)
    is_favorited = serializers.BooleanField(read_only=True)
    is_in_shopping_cart = serializers.BooleanField(read_only=True)
    image = Base64ImageField()
    ingredients = IngredientsSerializer(many=True)
    tags = TagsSerializer(many=True)

    class Meta:
        model = Recipe
        fields = (
            "id",
            "ingredients",
            "tags",
            "image",
            "name",
            "text",
            "cooking_time",
            "author",
            "pub_date",
            "is_favorited",
            "is_in_shopping_cart"
            )


class RecipePOSTUPDELSerializer(serializers.ModelSerializer):
    author = CustomUserSerializer(read_only=True)
    tags = serializers.PrimaryKeyRelatedField(queryset=Tags.objects.all(), many=True)
    ingredients =  AmountRecipeSerializer(many=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ("id", "ingredients", "tags", "image", "name", "text", "cooking_time", "author", "pub_date")
    

    def create_ingredients(self, ingredients, recipe):
        new_ingredient = [
            IngredientInRecipe(
                recipe=recipe,
                ingredient=ingredient.get("id"),
                amount=ingredient.get("amount")
            )
            for ingredient in ingredients
        ]
        IngredientInRecipe.objects.bulk_create(new_ingredient)

    
    @transaction.atomic
    def create(self, validated_data):
        ingredients = validated_data.pop("ingredients")
        tags = validated_data.pop("tags")
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.create_ingredients(ingredients, recipe)
        return recipe        

    
    @transaction.atomic
    def update(self, instance, validated_data):          
        instance.name = validated_data.get("name", instance.name)
        instance.image = validated_data.get("image", instance.image)
        instance.text = validated_data.get("text", instance.text)
        instance.cooking_time= validated_data.get("cooking_time", instance.cooking_time)
        instance.tags.clear()
        instance.ingredients.clear()
        tags = self.validated_data.get("tags")
        instance.tags.set(tags)
        IngredientInRecipe.objects.filter(recipe=instance).all().delete()
        self.create_ingredients(validated_data.get("ingredients"), instance)
        instance.save()
        return instance
    
    def to_representation(self, obj):
        return RecipeListSerializer(obj, context=self.context).data
    

class FollowSerializer(CustomUserSerializer):
    count_recipes = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()


    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "count_recipes",
            "recipes",
            'is_subscribed',
            "email"
        )

    def get_count_recipes(self, obj):
        return obj.recipes.count()
        # return Recipe.objects.filter(author=obj.author).count()
    
    def get_recipes(self, obj):
        request = self.context.get("request")
        limit = request.query_params.get("recipes_limit")
        if limit:
            return RecipeInfoSerializer(
                Recipe.objects.filter(author=obj)[:int(limit)],
                many=True,
                context={"request": request}
            ).data
        return RecipeInfoSerializer(
            Recipe.objects.filter(author=obj),
            many=True,
            context={"request": request}
        ).data
    


class FollowListSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Follow
        fields = ("id", "user", "author")
        


class RecipeInfoSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ("id", "name", "image", "cooking_time")
        read_only_fields = fields
    

class FavouritesSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Favourite
        fields = ("id", "recipe", "user")


class ShoppingCartSerializer(serializers.ModelSerializer):

    class Meta:
        model = ShoppingCart
        fields = ("recipe", "user")

