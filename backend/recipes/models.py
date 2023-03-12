from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models

User = get_user_model()

class Tags(models.Model):
    name = models.CharField(
        unique=True,
        max_length=200,
        verbose_name="Название тэга"
    )
    color = models.CharField(
        max_length=7,
        verbose_name="Цвет в HEX",
        validators=[RegexValidator(
            regex=r"^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$",
            message="Цвет тэга содержит недопустимый символ"
        )],
    )
    slug = models.SlugField(
        unique=True,
        verbose_name="Слаг тэга"
    )
    
    class Meta:
        ordering = ("name", )
        verbose_name = "Тэг"
        verbose_name_plural = "Тэги"

    def __str__(self):
        return f"{self.name}"


class Ingredients(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name="Название ингредиента"
    )
    measurement_unit = models.CharField(
        max_length=200,
        verbose_name="Единица измерения"
    )

    class Meta:
        ordering = ("id", )
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"
        constraints = [
            models.UniqueConstraint(
                fields=["name", "measurement_unit"],
                name="uniqie_name_for_measurement_unit",
            ),
        ]

    def __str__(self):
        return f"{self.name}"


class Recipe(models.Model):
    ingredients = models.ManyToManyField(
        Ingredients,
        through="IngredientInRecipe",
        related_name="recipes",
        verbose_name="Ингдедиент"
    )
    tags = models.ManyToManyField(
        Tags,
        verbose_name="Тэги",
        related_name="recipes"
    )
    image = models.ImageField(
        upload_to='recipes/static/',
        help_text="Вставьте изображение",
        verbose_name="Изображение",
        blank=True,
        null=True
    )
    name = models.CharField(
        max_length=200,
        verbose_name="Название"
    )
    text = models.TextField(
        verbose_name="Описание"
    )
    cooking_time = models.PositiveIntegerField(
        validators=[
            MinValueValidator(1, message="минимальное время приготовления 1 м.")
        ],
        verbose_name="Время приготовления в минутах",
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата публикации"
    )
    author = models.ForeignKey(
        User,
        on_delete= models.CASCADE,
        verbose_name="Автор",
        related_name="recipes"
    )

    class Meta:
        ordering = ("-pub_date", )
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"
    
    def __str__(self):
        return f"{self.name}"


class IngredientInRecipe(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="recipe"
    )
    ingredient = models.ForeignKey(
        Ingredients,
        on_delete=models.CASCADE,
        related_name="ingredient",
        verbose_name="Ингредиент"
    )
    amount = models.PositiveIntegerField(
        default=1,
        validators=[
        MinValueValidator(1, message="Минимальное количество ингредиента 1")
        ],
        verbose_name="Количество ингредиентов в рецепте"
    )

    class Meta:
        verbose_name = "Количнство ингредиента"
        verbose_name_plural = "Количество ингредиентов"
        constraints = [
            models.UniqueConstraint(
                fields=["ingredient", "recipe"],
                name="uniqie_ingredient",
            ),
        ]

    def __str__(self):
        return f"{self.recipe} {self.ingredient} {self.amount}"


class Favourite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="favourites",
        verbose_name="Пользователь"
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="favourites",
        verbose_name="Рецепт"
    )

    class Meta:
        verbose_name = "Избранный рецепт",
        verbose_name_plural = "Избранные рецепты"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "recipe"],
                name="uniqie_recipe_for_user_in_shopping_cart",
            ),
        ]

    def __str__(self):
        return f"{self.user} добавил в избранное: {self.recipe.name}"
    

class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="shopping_cart_user",
        verbose_name="Пользователь"
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="shopping_cart_recipe",
        verbose_name="Рецепт"
    )

    class Meta:
        verbose_name = "Покупка",
        verbose_name_plural = "Покупки"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "recipe",],
                name="uniqie_fav_recipe_for_user",
            ),
        ]

    def __str__(self):       
        return f"{self.user} добавил в корзину: {self.recipe}"
