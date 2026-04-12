from rest_framework.routers import SimpleRouter

from .views import ShopCategoryViewSet

app_name = "v1_shop"

router = SimpleRouter()
router.register('shop_category', ShopCategoryViewSet, basename='shop_category')

urlpatterns = router.urls
