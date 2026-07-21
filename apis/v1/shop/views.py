from django.db.models import Prefetch, ExpressionWrapper, F, DecimalField
from rest_framework.exceptions import NotFound
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, DestroyModelMixin, CreateModelMixin
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.viewsets import ReadOnlyModelViewSet, ModelViewSet, GenericViewSet
from rest_framework.generics import ListAPIView, RetrieveAPIView, get_object_or_404

from apps.shop_app.models import (
    Category,
    Product,
    Sales,
    ProductImage,
    ProductAttributeValue,
    ProductComment,
    Order,
    OrderItem
)
from .serializers import (
    ShopCategorySerializer,
    RecommenderProductSerializer,
    MostProductSaleSerializer,
    MostProductDiscountSerializer,
    DetailProductSerializer,
    ProductCommentSerializer,
    CreateOrderBatchSerializer,
    OrderSerializer,
    OrderItemSerializer,
    AddOrderItemSerializer
)
from apis.utils.custom_permissions import IsOwnerProductComment
from apis.utils.paginations import CustomPagination, LatestItemPagination


class ShopCategoryViewSet(ReadOnlyModelViewSet):
    serializer_class = ShopCategorySerializer
    queryset = Category.objects.filter(is_active=True).select_related('parent').only(
        "parent__name",
        "name",
        "slug",
        "created_at",
        "updated_at",
        "category_image__image"
    ).select_related("category_image")


class RecommenderProductView(ListAPIView):
    serializer_class = RecommenderProductSerializer
    filterset_fields = ("is_amazing",)
    pagination_class = LatestItemPagination

    def get_queryset(self):
        fields = self.serializer_class.Meta.fields
        return  Product.objects.filter(
            is_amazing=True,
            is_active=True
        ).only(*fields).order_by('-updated_at').prefetch_related(
            Prefetch(
                "product_image",
                queryset=ProductImage.objects.filter(is_active=True).select_related("image").only("product_id", "image__image"),
            )
        )


class MostProductSaleView(ListAPIView):
    serializer_class = MostProductSaleSerializer
    pagination_class = LatestItemPagination

    def get_queryset(self):
        fields = ("product__product_slug", "product__price", "product__new_price", "product__product_name")
        p_img_fields = ("image__image", "product_id")
        return Sales.objects.filter(
            is_active=True
        ).select_related(
            "product"
        ).only(
            *fields
        ).order_by(
            '-quantity'
        ).prefetch_related(
            Prefetch(
                "product__product_image",
                queryset=ProductImage.objects.only(*p_img_fields).select_related("image").filter(is_active=True).order_by("order")
            )
        )


class MostProductDiscountView(ListAPIView):
    serializer_class = MostProductDiscountSerializer
    pagination_class = LatestItemPagination

    def get_queryset(self):
        fields = ("product_slug", "price", "new_price", "product_name", "category_id")
        p_img_fields = ("image__image", "product_id")
        return Product.objects.filter(
            is_active=True,
            new_price__isnull=False
        ).only(*fields).prefetch_related(
            Prefetch(
                "product_image",
                queryset=ProductImage.objects.only(*p_img_fields).select_related("image").filter(is_active=True).order_by("order")
            )
        ).annotate(
            discount_amount=ExpressionWrapper(
                F('price') - F('new_price'),
                output_field=DecimalField()
            )
        ).order_by("-discount_amount")


class DetailProductView(RetrieveAPIView):
    serializer_class = DetailProductSerializer

    def get_object(self):
        """
        Returns the object the view is displaying.

        You may want to override this if you need to provide non-standard
        queryset lookups.  Eg if objects are referenced using multiple
        keyword arguments in the url conf.
        """
        queryset = self.filter_queryset(self.get_queryset())

        # Perform the lookup filtering.
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field

        assert lookup_url_kwarg in self.kwargs, (
            'Expected view %s to be called with a URL keyword argument '
            'named "%s". Fix your URL conf, or set the `.lookup_field` '
            'attribute on the view correctly.' %
            (self.__class__.__name__, lookup_url_kwarg)
        )

        p_slug = self.kwargs.get("p_slug", None)
        if not p_slug:
            raise NotFound("product_slug must be specified")

        filter_kwargs = {self.lookup_field: self.kwargs[lookup_url_kwarg], "product_slug": p_slug}
        obj = get_object_or_404(queryset, **filter_kwargs)

        # May raise a permission denied
        self.check_object_permissions(self.request, obj)

        return obj


    def get_queryset(self):
        fields = ("category__name", "product_name", "price", "new_price", "product_slug", "description", "stock_number", "is_amazing", "created_at", "updated_at")
        p_img_fields = ("image__image", "product_id", "order")
        attr_fields = ("attribute_value__attribute__attribute_name", "product_id", "attribute_value__attribute_value")

        return Product.objects.filter(is_active=True).select_related("category").only(*fields).prefetch_related(
            Prefetch(
                "product_image",
                queryset=ProductImage.objects.filter(is_active=True).select_related("image").order_by("order").only(*p_img_fields)
            ),
            Prefetch(
                "product_attribute_values",
                queryset=ProductAttributeValue.objects.select_related("attribute_value__attribute").filter(is_active=True).only(*attr_fields)
            )
        ).annotate(
            discount_amount=ExpressionWrapper(
                F('price') - F('new_price'),
                output_field=DecimalField()
            )
        )


class ProductCommentViewSet(ModelViewSet):
    serializer_class = ProductCommentSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, IsOwnerProductComment)
    pagination_class = CustomPagination
    lookup_field = 'id'

    def get_queryset(self):
        fields = ("user__username", "created_at", "updated_at", "comment", "product_id")
        return ProductComment.objects.filter(
            is_active=True,
            product_id=self.kwargs['pk'],
        ).select_related("user").only(*fields).order_by("-id")

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['product_id'] = self.kwargs['pk']
        return context

    def perform_destroy(self, instance):
        instance.is_active = False
        instance.save()


class OrderViewSet(ListModelMixin, RetrieveModelMixin, DestroyModelMixin, CreateModelMixin, GenericViewSet):
    permission_classes = (IsAuthenticated,)
    pagination_class = CustomPagination

    def get_serializer_class(self):
        if self.action == "create":
            return CreateOrderBatchSerializer
        else:
            return OrderSerializer

    def get_queryset(self):
        item_fields = ("quantity", "order_id", "product__product_name", "product__price", "product__new_price")
        p_img_fields = ("product_id", "image__image")

        return Order.objects.filter(
            is_active=True,
            user_id=self.request.user.id,
        ).order_by('-id').prefetch_related(
            Prefetch(
                "order_items",
                queryset=OrderItem.objects.filter(is_active=True).select_related("product").only(*item_fields)
            ),
            Prefetch(
                "order_items__product__product_image",
                queryset=ProductImage.objects.select_related("image").only(*p_img_fields).order_by('order').filter(is_active=True)
            )
        )

    def perform_destroy(self, instance):
        instance.is_active = False
        instance.save()


class OrderItemViewSet(ModelViewSet):
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        fields = ("product__product_name", "quantity", "product__price", "product__new_price", "order_id")
        p_img_fields = ("product_id", "image__image")

        return OrderItem.objects.filter(
            is_active=True,
            order_id=self.kwargs['order_pk']
        ).select_related("product").only(*fields).prefetch_related(
            Prefetch(
                "product__product_image",
                queryset=ProductImage.objects.filter(is_active=True).order_by('order').select_related("image").only(*p_img_fields)
            )
        )

    def get_serializer_class(self):
        if self.action == "create":
            return AddOrderItemSerializer
        else:
            return OrderItemSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['order_id'] = self.kwargs['order_pk']
        return context

    def perform_destroy(self, instance):
        instance.is_active = False
        instance.save()
