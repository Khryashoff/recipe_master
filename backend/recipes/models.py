from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from foodgram.settings import (COLOR_CHOISE, INGREDIENT_NAME, INGREDIENT_UNITS,
                               RECIPE_NAME, TAG_COLOR, TAG_NAME, TAG_SLUG)
from users.models import User


class Ingredients(models.Model):
    """
    Класс, представляющий ингредиенты.
    """
    name = models.CharField(
        verbose_name='Наименование ингредиента',
        max_length=INGREDIENT_NAME
    )
    measurement_unit = models.CharField(
        verbose_name='Единицы измерения ингредиента',
        max_length=INGREDIENT_UNITS
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self) -> str:
        return f'{self.name}, {self.measurement_unit}'


class TimeTag(models.Model):
    """
    Класс, представляющий временные метки для рецептов.
    """
    name = models.CharField(
        verbose_name='Название временной метки',
        max_length=TAG_NAME,
        unique=True
    )
    color = models.CharField(
        verbose_name='Цвет временной метки, стандарт HEX',
        max_length=TAG_COLOR,
        unique=True,
        choices=COLOR_CHOISE
    )
    slug = models.SlugField(
        verbose_name='Ссылка временной метки',
        max_length=TAG_SLUG,
        unique=True
    )

    class Meta:
        verbose_name = 'Временную метку'
        verbose_name_plural = 'Временные метки'

    def __str__(self):
        return self.name


class Recipes(models.Model):
    """
    Класс, представляющий рецепты.
    """
    author = models.ForeignKey(
        User,
        verbose_name='Создатель рецепта',
        on_delete=models.SET_NULL,
        null=True,
        related_name='recipes'
    )
    name = models.CharField(
        verbose_name='Название рецепта',
        max_length=RECIPE_NAME
    )
    tags = models.ManyToManyField(
        TimeTag,
        verbose_name='Временные метки рецепта',
        related_name='recipes'
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время для приготовления блюда',
        validators=[
            MinValueValidator(
                1, message='Время приготовления не может быть меньше 1 минуты!'
            ),
            MaxValueValidator(
                1440, message='Время приготовления не может быть больше 1 дня!'
            )
        ]
    )
    text = models.TextField(
        verbose_name='Описание рецепта',
    )
    ingredients = models.ManyToManyField(
        Ingredients,
        verbose_name='Список ингредиентов к рецепту',
        through='RecipeIngredients',
        related_name='recipes'
    )
    image = models.ImageField(
        verbose_name='Изображение готового блюда',
        upload_to='image_recipes/',
    )

    class Meta:
        ordering = ['-id']
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'name'],
                name='unique_author_recipe'
            ),
        ]

    def __str__(self) -> str:
        return self.name


class RecipeIngredients(models.Model):
    """
    Класс, связывающий рецепт и ингредиенты для рецепта.
    """
    recipe = models.ForeignKey(
        Recipes,
        verbose_name='Используемый рецепт',
        on_delete=models.CASCADE,
        related_name='recipe_ingredients'
    )
    ingredient = models.ForeignKey(
        Ingredients,
        verbose_name='Используемые ингредиенты',
        on_delete=models.CASCADE
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество',
        validators=[
            MinValueValidator(
                1, message='Минимальное количество 1!'
            )
        ]
    )

    class Meta:
        verbose_name = 'Ингредиент для рецепта'
        verbose_name_plural = 'Ингредиенты для рецепта'

    def __str__(self) -> str:
        return (
            f'{self.ingredient.name} {self.ingredient.measurement_unit}'
            f' - {self.amount} '
        )


class Favorites(models.Model):
    """
    Класс, представляющий избранное.
    """
    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        on_delete=models.CASCADE,
        related_name='favorites'
    )
    recipe = models.ForeignKey(
        Recipes,
        verbose_name='Список рецептов',
        on_delete=models.CASCADE,
        related_name='favorites'
    )

    class Meta:
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранное'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_favorites'
            )
        ]

    def __str__(self) -> str:
        return f'{self.user} добавляет {self.recipe} в избранное'


class Shoplist(models.Model):
    """
    Класс, представляющий список покупок.
    """
    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        on_delete=models.CASCADE,
        related_name='shoplist'
    )
    recipe = models.ForeignKey(
        Recipes,
        verbose_name='Список рецептов',
        on_delete=models.CASCADE,
        related_name='shoplist'
    )

    class Meta:
        ordering = ['-id']
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_recipe_shoplist'
            )
        ]

    def __str__(self) -> str:
        return f'{self.user} добавляет {self.recipe} в список покупок'
