from django.contrib import admin

from .models import Subscribe, User


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
        'date_joined'
    )
    list_filter = (
        'username',
        'email'
    )
    search_fields = (
        'username',
        'email'
    )
    empty_value_display = '-empty-'


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


admin.site.register(User, UserAdmin)
admin.site.register(Subscribe, SubscribeAdmin)
