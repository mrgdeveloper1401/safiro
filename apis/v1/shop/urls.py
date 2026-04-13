from django.urls import path
from rest_framework.routers import SimpleRouter

from .views import ShopCategoryViewSet, IsAmazingView

app_name = "v1_shop"

router = SimpleRouter()
router.register('shop_category', ShopCategoryViewSet, basename='shop_category')

urlpatterns = [
    path("amazing_product/", IsAmazingView.as_view(), name='is_amazing_product'),
] + router.urls
