from rest_framework.pagination import PageNumberPagination


class NetWorkPagination(PageNumberPagination):
    """ Пагинатор для объектов сети с поддержкой настройки размера страницы через параметр `page_size` """
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100
