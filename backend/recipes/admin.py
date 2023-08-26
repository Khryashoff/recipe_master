from django.contrib import admin

from .models import Favorites, Ingredients, Recipes, Shoplist, TimeTag


@admin.register(Ingredients)
class IngredientsAdmin(admin.ModelAdmin):
    """
    Класс, для настройки административного интерфейса модели Ingredients.
    """
    list_display = [
        'id',
        'name',
        'measurement_unit',
    ]
    list_filter = ('name',)
    search_fields = ('name',)


@admin.register(TimeTag)
class TimeTagAdmin(admin.ModelAdmin):
    """
    Класс, для настройки административного интерфейса модели TimeTag.
    """
    list_display = [
        'id',
        'name',
        'color',
        'slug',
    ]
    search_fields = ('name',)
    list_filter = ('name',)


@admin.register(Recipes)
class RecipesAdmin(admin.ModelAdmin):
    """
    Класс, для настройки административного интерфейса модели Recipes.
    """
    list_display = (
        'id',
        'name',
        'author',
        'favorite_counter'
    )
    search_fields = (
        'name',
        'author',
        'tags'
    )
    list_filter = (
        'name',
        'author',
        'tags'
    )
    ordering = ('-id',)

    @admin.display(description='Находится в избранном')
    def favorite_counter(self, obj):
        return obj.favorites.all().count()


@admin.register(Favorites)
class FavoritesAdmin(admin.ModelAdmin):
    """
    Класс, для настройки административного интерфейса модели Favorites.
    """
    list_display = (
        'id',
        'user',
        'recipe'
    )
    search_fields = ('user',)
    list_filter = ('user',)


@admin.register(Shoplist)
class ShoplistAdmin(admin.ModelAdmin):
    """
    Класс, для настройки административного интерфейса модели Shoplist.
    """
    list_display = (
        'id',
        'user',
        'recipe'
    )
    search_fields = ('user',)
    list_filter = ('user',)
