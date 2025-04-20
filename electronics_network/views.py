from django_filters import rest_framework as filters
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets
from rest_framework.exceptions import ValidationError

from electronics_network.filters import SupplyChainMemberFilter
from electronics_network.models import Product, SupplyChainMember
from electronics_network.paginators import NetWorkPagination
from electronics_network.serializers import SupplyChainMemberSerializer, ProductSerializer
from users.permissions import IsActiveEmployeeOrAdmin


class ProductViewSet(viewsets.ModelViewSet):
    """ CRUD операции для модели `Product` """

    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    pagination_class = NetWorkPagination
    permission_classes = (IsActiveEmployeeOrAdmin,)


class SupplyChainMemberViewSet(viewsets.ModelViewSet):
    """ CRUD операции для модели `SupplyChainMember` """

    queryset = SupplyChainMember.objects.all()
    serializer_class = SupplyChainMemberSerializer
    pagination_class = NetWorkPagination
    permission_classes = (IsActiveEmployeeOrAdmin,)
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = SupplyChainMemberFilter

    @swagger_auto_schema(  # добавление информации о параметре фильтрации `country` в API документацию
        manual_parameters=[
            openapi.Parameter(
                'country',
                openapi.IN_QUERY,
                description='Filter by country',
                type=openapi.TYPE_STRING
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def perform_create(self, serializer):
        """ Создание поставщика с автоматическим добавлением текущего пользователя """
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        """ Обновление объекта с запретом обновления поля `debt` через API """
        if 'debt' in serializer.validated_data:
            raise ValidationError({'debt': "Обновление поля 'Задолженность' запрещено через API."})
        serializer.save()
