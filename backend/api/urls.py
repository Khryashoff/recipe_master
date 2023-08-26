from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import (ActionUserViewSet, IngredientsViewSet, RecipesViewSet,
                       TimeTagViewSet)

app_name = 'api'

router_v1 = DefaultRouter()
router_v1.register(r'users', ActionUserViewSet, basename='users')
router_v1.register(r'tags', TimeTagViewSet, basename='tags')
router_v1.register(r'recipes', RecipesViewSet, basename='recipes')
router_v1.register(r'ingredients', IngredientsViewSet, basename='ingredients')

urlpatterns = [
    path('', include(router_v1.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
