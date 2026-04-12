from rest_framework.viewsets import ReadOnlyModelViewSet

from apps.shop_app.models import Category
from .serializers import ShopCategorySerializer


class ShopCategoryViewSet(ReadOnlyModelViewSet):
    serializer_class = ShopCategorySerializer
    queryset = Category.objects.filter(is_active=True).select_related('parent').only(
        "parent__name",
        "name",
        "slug",
        "created_at",
        "updated_at",
    )

