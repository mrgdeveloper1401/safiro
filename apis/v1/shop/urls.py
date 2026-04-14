from django.urls import path
from rest_framework.routers import SimpleRouter

from .views import (
    ShopCategoryViewSet,
    RecommenderProductView,
    MostProductSaleView,
    MostProductDiscountView,
    DetailProductView
)

app_name = "v1_shop"

router = SimpleRouter()
router.register('shop_category', ShopCategoryViewSet, basename='shop_category')

urlpatterns = [
    path("recommender_product/", RecommenderProductView.as_view(), name='is_amazing_product'),
    path("most_product_sale/", MostProductSaleView.as_view(), name='is_amazing_product'),
    path("most_product_discount/", MostProductDiscountView.as_view(), name='is_amazing_product'),
    path("detail_product/<int:pk>/", DetailProductView.as_view(), name='detail_product'),
] + router.urls
