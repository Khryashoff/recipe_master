from django_filters.rest_framework import FilterSet, filters

from recipes.models import Ingredients, Recipes, TimeTag


class IngredientsFilter(FilterSet):
    """
    Фильтр для модели Ingredients.
    """
    name = filters.CharFilter(lookup_expr='startswith')

    class Meta:
        model = Ingredients
        fields = ['name']


class RecipesFilter(FilterSet):
    """
    Фильтр для модели Recipes.
    """
    tags = filters.ModelMultipleChoiceFilter(
        queryset=TimeTag.objects.all(),
        field_name='tags__slug',
        to_field_name='slug',
    )
    author = filters.NumberFilter(
        field_name='author__id',
    )
    is_favorited = filters.BooleanFilter(method='get_is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(
        method='get_is_in_shopping_cart'
    )

    class Meta:
        model = Recipes
        fields = [
            'tags',
            'author',
        ]

    def get_is_favorited(self, queryset, name, value):
        """
        Фильтрует рецепты по наличию в избранном у пользователя.
        """
        if value and not self.request.user.is_anonymous:
            return queryset.filter(favorites__user=self.request.user)
        return queryset

    def get_is_in_shopping_cart(self, queryset, name, value):
        """
        Фильтрует рецепты по наличию в корзине покупок у пользователя.
        """
        if value and not self.request.user.is_anonymous:
            return queryset.filter(shoplist__user=self.request.user)
        return queryset
