from django.contrib.auth.hashers import make_password
from django.db import IntegrityError
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from foodgram.settings import ALLOWED_ACTIONS
from recipes.models import (Favorites, Ingredients, RecipeIngredients, Recipes,
                            Shoplist, TimeTag)
from rest_framework.decorators import action
from rest_framework.permissions import SAFE_METHODS, IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import (HTTP_200_OK, HTTP_201_CREATED,
                                   HTTP_204_NO_CONTENT, HTTP_400_BAD_REQUEST,
                                   HTTP_401_UNAUTHORIZED)
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from users.models import Subscribe, User

from api.filters import IngredientsFilter, RecipesFilter
from api.pagination import FoodgramPageNumberPagination
from api.permissions import AuthorOrReadOnly
from api.serializers import (CreateRecipeSerializer, IngredientsSerializer,
                             RecipesSerializer, SubscribeDetailSerializer,
                             SubscribeRecipesSerializer, TimeTagSerializer,
                             UsersSerializer)


class ActionUserViewSet(UserViewSet):
    """
    Набор представлений для работы с User и Subscribe.
    """
    queryset = User.objects.all()
    serializer_class = SubscribeDetailSerializer
    pagination_class = FoodgramPageNumberPagination

    @action(
        methods=['post'],
        detail=False,
        permission_classes=[IsAuthenticated]
    )
    def set_password(self, request, pk=None):
        """
        Обновляет пароль текущего пользователя.
        """
        user = self.request.user
        if user.is_anonymous:
            return Response(status=HTTP_401_UNAUTHORIZED)

        new_password = request.data.get('new_password')
        if not new_password:
            return Response(
                {'new_password': ['Это поле является обязательным!']},
                status=HTTP_400_BAD_REQUEST
            )

        user.password = make_password(new_password)
        user.save()

        return Response(status=HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        permission_classes=[IsAuthenticated]
    )
    def subscriptions(self, request):
        """
        Получает список подписок текущего пользователя.
        """
        user = request.user
        queryset = User.objects.filter(following__user=user)
        pages = self.paginate_queryset(queryset)
        serializer = SubscribeDetailSerializer(
            pages,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    @action(
        methods=['post', 'delete'],
        detail=True,
        permission_classes=[IsAuthenticated]
    )
    def subscribe(self, request, id):
        """
        Осуществляет подписку и отписку от другого пользователя.
        """
        user = self.request.user
        author = get_object_or_404(User, id=id)

        if user.is_anonymous:
            return Response(status=HTTP_401_UNAUTHORIZED)

        try:
            if request.method == 'POST':
                if user == author:
                    data = {'errors': 'Невозможно подписаться на самого себя!'}
                    return Response(
                        data=data,
                        status=HTTP_400_BAD_REQUEST
                    )

                Subscribe.objects.create(user=user, author=author)
                serializer = SubscribeDetailSerializer(
                    author,
                    context={'request': request}
                )
                return Response(
                    serializer.data,
                    status=HTTP_201_CREATED
                )

            elif request.method == 'DELETE':
                subscribe = Subscribe.objects.filter(user=user, author=author)
                if subscribe.exists():
                    subscribe.delete()
                    return Response(status=HTTP_204_NO_CONTENT)
                else:
                    data = {'errors': 'Данная подписка не существует!'}
                    return Response(
                        data=data,
                        status=HTTP_400_BAD_REQUEST
                    )

        except IntegrityError:
            data = {'errors': 'Вы уже подписались на этого пользователя!'}
            return Response(
                data=data,
                status=HTTP_400_BAD_REQUEST
            )

    def get_serializer_context(self):
        """
        Возвращает контекст для сериализатора текущего запроса.
        """
        return {'request': self.request}

    @action(
        methods=['get'],
        detail=False,
        permission_classes=[IsAuthenticated]
    )
    def me(self, request):
        """
        Получает информацию о текущем пользователе.
        """
        user = request.user
        if user.is_authenticated:
            serializer = UsersSerializer(
                user,
                context=self.get_serializer_context()
            )
            return Response(serializer.data, status=HTTP_200_OK)
        else:
            return Response(
                {'detail': 'Учетные данные не предоставлены.'},
                status=HTTP_401_UNAUTHORIZED
            )

    @me.mapping.post
    def me_post(self, request):
        """
        Обрабатывает 'POST' запросы для функции 'me'.
        """
        return self.me(request)


class TimeTagViewSet(ReadOnlyModelViewSet):
    """
    Набор представлений для работы с TimeTag.
    """
    queryset = TimeTag.objects.all()
    serializer_class = TimeTagSerializer
    permission_classes = (AuthorOrReadOnly,)


class IngredientsViewSet(ReadOnlyModelViewSet):
    """
    Набор представлений для работы с Ingredients.
    """
    queryset = Ingredients.objects.all()
    serializer_class = IngredientsSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientsFilter


class RecipesViewSet(ModelViewSet):
    """
    Набор представлений для работы с Recipes.
    """
    http_method_names = ALLOWED_ACTIONS
    queryset = Recipes.objects.all()
    pagination_class = FoodgramPageNumberPagination
    permission_classes = (AuthorOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipesFilter

    def perform_create(self, serializer):
        """
        Сохраняет автора при создании рецепта.
        """
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        """
        Определяет класс сериализатора в зависимости от метода запроса.
        """
        if self.request.method in SAFE_METHODS:
            return RecipesSerializer
        return CreateRecipeSerializer

    @action(
        methods=['post', 'delete'],
        detail=True,
        permission_classes=[IsAuthenticated]
    )
    def favorite(self, request, pk=None):
        """
        Позволяет пользователям добавлять и удалять рецепты из избранного.
        """
        if request.method == 'POST':
            return self.post_recipe(Favorites, request.user, pk)
        elif request.method == 'DELETE':
            return self.delete_recipe(Favorites, request.user, pk)
        return None

    @action(
        methods=['post', 'delete'],
        detail=True,
        permission_classes=[IsAuthenticated]
    )
    def shopping_cart(self, request, pk=None):
        """
        Позволяет пользователям добавлять и удалять рецепты из корзины покупок.
        """
        if request.method == 'POST':
            return self.post_recipe(Shoplist, request.user, pk)
        if request.method == 'DELETE':
            return self.delete_recipe(Shoplist, request.user, pk)
        return None

    def post_recipe(self, model, user, pk):
        """
        Общий метод для добавления рецепта в список (избранное, покупки).
        """
        if model.objects.filter(user=user, recipe_id=pk).exists():
            return Response(
                {'errors': 'Вы уже добавили этот рецепт'},
                status=HTTP_400_BAD_REQUEST
            )
        recipe = get_object_or_404(Recipes, id=pk)
        model.objects.create(user=user, recipe=recipe)
        serializer = SubscribeRecipesSerializer(recipe)
        return Response(serializer.data, status=HTTP_201_CREATED)

    def delete_recipe(self, model, user, pk):
        """
        Общий метод для удаления рецепта из списка (избранное, покупки).
        """
        obj = model.objects.filter(user=user, recipe__id=pk)
        if obj.exists():
            obj.delete()
            return Response(status=HTTP_204_NO_CONTENT)
        return Response(
            {'errors': 'Вы уже удалили этот рецепт'},
            status=HTTP_400_BAD_REQUEST
        )

    @action(
        methods=['get'],
        detail=False,
        permission_classes=[IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        """
        Формирует файл со списком покупок для скачивания.
        """
        cart_ingredients = (
            RecipeIngredients.objects.filter(
                recipe__shoplist__user=request.user
            ).values(
                'ingredient__name',
                'ingredient__measurement_unit',
            ).annotate(cart_amount=Sum('amount')).order_by('-amount')
        )

        shoplist = ''
        for num, item in enumerate(cart_ingredients):
            name = item['ingredient__name']
            measurement_unit = item['ingredient__measurement_unit']
            amount = item['cart_amount']
            shoplist += (f'{num + 1}. {name} - '
                         f'{amount} {measurement_unit} \n')

        filename = 'shoplist.txt'
        response = HttpResponse(shoplist,
                                content_type='text/plain,charset=utf8')
        response['Content-Disposition'] = f'attachment; filename={filename}'
        return response
