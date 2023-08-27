from rest_framework.pagination import PageNumberPagination


class FoodgramPageNumberPagination(PageNumberPagination):
    """
    Пагинация по номерам страниц для API Foodgram.

    Attributes:
        page_size (int): Количество элементов на странице по умолчанию.
        page_size_query_param (str): Параметр запроса для указания
        количества элементов на странице.
    """
    page_size_query_param = 'limit'
