import base64

import webcolors
from django.core.files.base import ContentFile
from django.db import transaction
from djoser.serializers import UserCreateSerializer, UserSerializer
# from django.shortcuts import get_object_or_404
from rest_framework import serializers

from recipes.models import (IngredientInRecipe, Ingredients, Recipe,
                            ShoppingCart, Tags)
from users.models import Follow, User

# User = get_user_model()


class CustomUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField(read_only=True)
    
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
        request = self.context.get("request")
        if request.user.is_anonymous:
            return False
        user = request.user
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


class RecipeREADSerializer(serializers.ModelSerializer):
    author = CustomUserSerializer(read_only=True)
    is_favorited = serializers.BooleanField(read_only=True)
    is_in_shopping_cart = serializers.BooleanField(read_only=True)
    image = Base64ImageField()
    ingredients = IngredientsSerializer(read_only=True, many=True)
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
    
    def get_is_favorited(self, obj):
        request = self.context.get("request")
        if request.user_is_anonymous:
            return False
        return request.user.favourites.filter(recipe=obj).exists()
    
    def get_is_in_shopping_cart(self, obj):
        request = self.context.get("request")
        if request.user_is_anonymous:
            return False
        return request.user.shopping_cart_user.filter(recipe=obj).exists()



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
        tags = self.initial_data.get("tags")
        instance.tags.set(tags)
        IngredientInRecipe.objects.filter(recipe=instance).all().delete()
        ingredients = validated_data.get("ingredients")
        self.create_ingredients(ingredients, instance)
        instance.save()
        return instance
    
    def to_representation(self, obj):
        return RecipeREADSerializer(obj, context=self.context).data
    

class FollowSerializer(CustomUserSerializer):
    email = serializers.ReadOnlyField(source="author.email")
    id = serializers.ReadOnlyField(source="author.id")
    first_name = serializers.ReadOnlyField(source="author.first_name")
    last_name = serializers.ReadOnlyField(source="author.last_name")
    author = serializers.ReadOnlyField(source="author.username")
    count_recipes = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    image = serializers.ReadOnlyField(source="author.image")

    class Meta:
        model = User
        fields = (
            "id",
            "author",
            "username",
            "first_name",
            "last_name",
            "email",
            "count_recipes",
            "recipes",
            "image"
        )
    
    def get_count_recipes(self, obj):
        # return obj.recipes.count()
        return Recipe.objects.filter(author=obj.author).count()
    
    def get_recipes(self, obj):
        queryset = Recipe.objects.filter(author=obj.author)
        return RecipeInfoSerializer(queryset, many=True)


class RecipeInfoSerializer(serializers.ModelSerializer):
    # image = Base64ImageField

    class Meta:
        model = Recipe
        fields = ("id", "name", "image", "cooking_time")
    

class FavouritesSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Recipe
        fields = ("id", "name", "image")


class ShoppingCartSerializer(serializers.ModelSerializer):

    class Meta:
        model = ShoppingCart
        fields = ("recipe", "user")

