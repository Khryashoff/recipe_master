import re

from djoser.serializers import UserSerializer
from drf_extra_fields.fields import Base64ImageField
from foodgram.settings import PASSWORD
from recipes.models import (Favorites, Ingredients, RecipeIngredients, Recipes,
                            Shoplist, TimeTag)
from rest_framework import serializers
from rest_framework.validators import (UniqueTogetherValidator,
                                       UniqueValidator, ValidationError)
from users.models import Subscribe, User


class UsersSerializer(UserSerializer):
    """
    Сериализатор модели Users.
    """
    username = serializers.CharField(
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    email = serializers.EmailField(
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    password = serializers.CharField(
        max_length=PASSWORD,
        write_only=True
    )

    class Meta:
        model = User
        fields = [
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password',
        ]
        extra_kwargs = {
            'email': {'required': True},
            'username': {'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
            'password': {'required': True},
        }
        validators = [
            UniqueTogetherValidator(
                queryset=User.objects.all(),
                fields=('email', 'username'),
                message='Email и Username должны быть уникальными'
            )
        ]

    def create(self, validated_data):
        """
        Создает нового пользователя.
        """
        return User.objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        """
        Обновляет и сохраняет изменения в экземпляре пользователя.
        """
        password = validated_data.get('password')
        if password:
            instance.set_password(password)
        instance.save()
        return instance


class SubscribeRecipesSerializer(serializers.ModelSerializer):
    """
    Сериализатор модели Recipes для взаимодействия с подписками.
    """
    image = Base64ImageField()

    class Meta:
        model = Recipes
        fields = [
            'id',
            'name',
            'image',
            'cooking_time',
        ]


class SubscribeDetailSerializer(UsersSerializer):
    """
    Сериализатор модели User для получения информации о подписках.
    """
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'email', 'username', 'first_name', 'last_name',
            'recipes', 'recipes_count', 'is_subscribed',
        ]
        read_only_fields = [
            'id', 'email', 'username', 'first_name', 'last_name',
            'recipes', 'recipes_count', 'is_subscribed',
        ]

    def get_is_subscribed(self, obj):
        """
        Определяет, подписан ли текущий аутентифицированный
        пользователь на объект.
        """
        user = self.context['request'].user
        if user.is_authenticated:
            return Subscribe.objects.filter(
                author=user,
                user=obj
            ).exists()
        return False

    def get_recipes(self, obj):
        limit = self.context['request'].query_params.get('recipes_limit')
        recipes = (
            obj.recipes.all()[:int(limit)]
            if limit is not None else obj.recipes.all()
        )
        return SubscribeRecipesSerializer(recipes, many=True).data

    def get_recipes_count(self, obj):
        """
        Возвращает общее количество рецептов,
        на которые подписан пользователь.
        """
        return obj.recipes.all().count()


class SubscribeSerializer(serializers.ModelSerializer):
    """
    Сериализатор модели Subscribe.
    """
    class Meta:
        model = Subscribe
        fields = [
            'author',
            'user',
        ]
        validators = (
            UniqueTogetherValidator(
                queryset=Subscribe.objects.all(),
                fields=('author', 'user'),
                message=('Вы уже подписались на этого автора')
            ),
        )

    def validate(self, data):
        """
        Проверяет, не подписывается ли пользователь на самого себя.
        """
        if data.get('author') == data.get('user'):
            raise ValidationError(
                {'errors': 'Нельзя подписываться на самого себя'})
        return data

    def create(self, validated_data):
        """
        Создает новую подписку на автора рецептов.
        """
        return Subscribe.objects.create(**validated_data)

    def to_representation(self, instance):
        """
        Возвращает данные о подписке в сериализованном виде.
        """
        return SubscribeDetailSerializer(
            instance=instance.user,
            context=self.context
        ).data


class TimeTagSerializer(serializers.ModelSerializer):
    """
    Сериализатор модели TimeTag.
    """
    class Meta:
        model = TimeTag
        fields = '__all__'
        read_only_fields = [
            'name',
            'color',
            'slug',
        ]


class IngredientsSerializer(serializers.ModelSerializer):
    """
    Сериализатор модели Ingredients.
    """
    class Meta:
        model = Ingredients
        fields = '__all__'


class RecipeIngredientsSerializer(serializers.ModelSerializer):
    """
    Сериализатор модели RecipeIngredients.
    """
    id = serializers.ReadOnlyField(
        source='ingredient.id'
    )
    name = serializers.ReadOnlyField(
        source='ingredient.name'
    )
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')

    class Meta:
        model = RecipeIngredients
        fields = [
            'id',
            'name',
            'measurement_unit',
            'amount',
        ]


class RecipesSerializer(serializers.ModelSerializer):
    """
    Сериализатор модели Recipes.
    """
    author = UsersSerializer(
        read_only=True
    )
    tags = TimeTagSerializer(
        read_only=True,
        many=True
    )
    ingredients = RecipeIngredientsSerializer(
        many=True,
        source='recipe_ingredients'
    )
    is_favorited = serializers.SerializerMethodField(
        read_only=True
    )
    is_in_shopping_cart = serializers.SerializerMethodField(
        read_only=True
    )
    image = Base64ImageField()

    class Meta:
        model = Recipes
        fields = [
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        ]

    def get_is_favorited(self, recipe):
        """
        Проверяет, находится ли рецепт в избранном у пользователя.
        """
        user = self.context.get('request').user
        return not user.is_anonymous and Favorites.objects.filter(
            recipe=recipe, user=user).exists()

    def get_is_in_shopping_cart(self, recipe):
        """
        Проверяет, находится ли рецепт в списке покупок у пользователя.
        """
        user = self.context.get('request').user
        return not user.is_anonymous and Shoplist.objects.filter(
            recipe=recipe, user=user).exists()


class CreateRecipeIngredientsSerializer(serializers.ModelSerializer):
    """
    Сериализатор связывающий модели Recipe и Ingredients.
    """
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredients.objects.all(), validators=[
            UniqueValidator(queryset=Ingredients.objects.all())
        ]
    )
    amount = serializers.IntegerField(min_value=1)

    class Meta:
        model = RecipeIngredients
        fields = [
            'id',
            'amount',
        ]


class CreateRecipeSerializer(serializers.ModelSerializer):
    """
    Сериализатор для создания и обновления рецептов.
    """
    image = Base64ImageField()
    author = UsersSerializer(read_only=True)
    ingredients = CreateRecipeIngredientsSerializer(
        many=True
    )

    class Meta:
        model = Recipes
        fields = '__all__'

    def validate_name(self, data):
        """
        Проверяет название рецепта на соответствие требованиям.
        """
        pattern = r'[а-яА-ЯёЁa-zA-Z\s]+$'
        if not re.fullmatch(pattern, data):
            raise ValidationError(
                'Название рецепта должно содержать только буквы и пробелы'
            )
        return data

    def validate(self, data):
        """
        Проверяет передаваемые данные о рецепте.
        """
        ingredients = data.get('ingredients')
        ingredient_list = []
        for ingredient in ingredients:
            ingredient_id = ingredient['id']
            if ingredient_id in ingredient_list:
                raise ValidationError({
                    'ingredients': 'Вы уже добавили этот ингредиент'
                })
            ingredient_list.append(ingredient_id)
            amount = ingredient['amount']
            if int(amount) < 1:
                raise ValidationError({
                    'amount': 'Введите правильное количество'
                })

        tags = data.get('tags')
        if not tags:
            raise ValidationError({
                'tags': 'Выберите временную метку'
            })
        tags_list = []
        for tag in tags:
            if tag in tags_list:
                raise ValidationError({
                    'tags': 'Вы уже добавили эту временную метку'
                })
            tags_list.append(tag)

        cooking_time = data.get('cooking_time')
        try:
            if int(cooking_time) < 1:
                raise ValueError()
        except (ValueError, TypeError):
            raise ValidationError({
                'cooking_time': 'Введите правильное время приготовления'
            })
        return data

    def add_ingredients(self, ingredients_data, recipe):
        """
        Добавляет ингредиенты к рецепту.
        """
        for ingredient in ingredients_data:
            RecipeIngredients.objects.create(
                recipe=recipe,
                amount=ingredient['amount'],
                ingredient=ingredient['id']
            )

    def add_tags(self, tags, recipe):
        """
        Добавляет временные метки к рецепту.
        """
        for tag in tags:
            recipe.tags.add(tag)

    def create(self, validated_data):
        """
        Создает новый рецепт.
        """
        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')
        image_data = validated_data.pop('image')
        recipe = Recipes.objects.create(image=image_data, **validated_data)
        self.add_tags(tags_data, recipe)
        self.add_ingredients(ingredients_data, recipe)
        return recipe

    def update(self, instance, validated_data):
        """
        Обновляет существующий рецепт.
        """
        instance.tags.clear()
        RecipeIngredients.objects.filter(recipe=instance).delete()
        self.add_tags(validated_data.pop('tags'), instance)
        self.add_ingredients(validated_data.pop('ingredients'), instance)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        """
        Преобразует данные о рецепте в сериализованный вид.
        """
        request = self.context.get('request')
        context = {'request': request}
        return RecipesSerializer(
            instance, context=context).data
