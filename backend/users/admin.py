from django.contrib import admin
from django.db.models import Count

from .models import Subscribe, User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """
    Класс, для настройки административного интерфейса модели User.
    """
    list_display = (
        'id',
        'email',
        'username',
        'first_name',
        'last_name',
        'get_recipes_count',
        'get_followers_count'
    )
    list_filter = (
        'username',
        'email'
    )
    search_fields = (
        'username',
        'email'
    )

    def get_recipes_count(self, obj):
        """
        Возвращает количество рецептов, созданных пользователем.
        """
        return obj.recipes.count()

    def get_followers_count(self, obj):
        """
        Возвращает количество подписчиков данного пользователя.
        """
        return obj.follower.count()

    get_recipes_count.short_description = 'Количество рецептов'
    get_followers_count.short_description = 'Количество подписчиков'

    def get_queryset(self, request):
        """
        Переопределяет базовый queryset для объектов класса User.
        """
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(
            recipe_count=Count('recipes', distinct=True),
            follower_count=Count('follower', distinct=True)
        )
        return queryset


@admin.register(Subscribe)
class SubscribeAdmin(admin.ModelAdmin):
    """
    Класс, для настройки административного интерфейса модели Subscribe.
    """
    list_display = (
        'id',
        'author',
        'user'
    )
    search_fields = ('user',)
    list_filter = ('user', )
    empty_value_display = '-empty-'
