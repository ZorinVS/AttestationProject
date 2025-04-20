import django_filters

from electronics_network.models import SupplyChainMember


class SupplyChainMemberFilter(django_filters.FilterSet):
    """ Фильтр для участников цепочки поставок по стране из контактных данных """
    country = django_filters.CharFilter(field_name='contact__country', lookup_expr='icontains')

    class Meta:
        model = SupplyChainMember
        fields = ['country']
