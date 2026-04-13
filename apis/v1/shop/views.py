from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.generics import ListAPIView

from apps.shop_app.models import Category, Product
from .serializers import ShopCategorySerializer, IsAmazingProductSerializer


class ShopCategoryViewSet(ReadOnlyModelViewSet):
    serializer_class = ShopCategorySerializer
    queryset = Category.objects.filter(is_active=True).select_related('parent').only(
        "parent__name",
        "name",
        "slug",
        "created_at",
        "updated_at",
    )


class IsAmazingView(ListAPIView):
    serializer_class = IsAmazingProductSerializer

    def get_queryset(self):
        fields = self.serializer_class.Meta.fields
        return  Product.objects.filter(is_amazing=True, is_active=True).only(*fields).order_by('-updated_at')[:10]
