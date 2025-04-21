from rest_framework.routers import DefaultRouter

from electronics_network.apps import ElectronicsNetworkConfig
from electronics_network.views import ProductViewSet, SupplyChainMemberViewSet

app_name = ElectronicsNetworkConfig.name

router = DefaultRouter()
router.register(r'suppliers', SupplyChainMemberViewSet, basename='supplier')
router.register(r'products', ProductViewSet, basename='product')


urlpatterns = [] + router.urls
