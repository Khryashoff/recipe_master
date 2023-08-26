import django_filters
from django_filters import filters
from recipes.models import Ingredients, Recipes, TimeTag


class IngredientsFilter(django_filters.FilterSet):
    """
    Фильтр для модели Ingredients.
    """
    name = django_filters.CharFilter(lookup_expr='istartswith')

    class Meta:
        model = Ingredients
        fields = ['name']


class RecipesFilter(django_filters.FilterSet):
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
    is_favorites = filters.BooleanFilter(method='get_is_favorites')
    is_in_shopping_cart = filters.BooleanFilter(
        method='get_is_in_shopping_cart'
    )

    class Meta:
        model = Recipes
        fields = [
            'tags',
            'author',
            'is_favorites',
            'is_in_shopping_cart',
        ]

    def get_is_favorites(self, queryset, name, value):
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
