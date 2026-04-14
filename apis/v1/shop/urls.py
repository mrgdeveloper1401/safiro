from django.urls import path
from rest_framework.routers import SimpleRouter
from rest_framework_nested.routers import NestedSimpleRouter

from .views import (
    ShopCategoryViewSet,
    RecommenderProductView,
    MostProductSaleView,
    MostProductDiscountView,
    DetailProductView,
    ProductCommentViewSet,
    OrderViewSet,
    OrderItemViewSet
)

app_name = "v1_shop"

router = SimpleRouter()
router.register('shop_category', ShopCategoryViewSet, basename='shop_category')
router.register("order", OrderViewSet, basename='order')

order_router = NestedSimpleRouter(router, r'order', lookup='order')
order_router.register('order_item', OrderItemViewSet, basename='order_item')

urlpatterns = [
    path("recommender_product/", RecommenderProductView.as_view(), name='is_amazing_product'),
    path("most_product_sale/", MostProductSaleView.as_view(), name='is_amazing_product'),
    path("most_product_discount/", MostProductDiscountView.as_view(), name='is_amazing_product'),
    path("detail_product/<int:pk>/<str:p_slug>/", DetailProductView.as_view(), name='detail_product'),
    path("detail_product/<int:pk>/<str:p_slug>/comment/", ProductCommentViewSet.as_view({'get': 'list', "post": "create"}), name='product_comment'),
    path("detail_product/<int:pk>/<str:p_slug>/comment/<int:id>", ProductCommentViewSet.as_view({'get': 'retrieve', "delete": "destroy", "patch": "update", 'put': 'update'}), name='product_comment_detail'),
] + router.urls + order_router.urls
