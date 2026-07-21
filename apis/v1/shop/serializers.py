from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers
from rest_framework.exceptions import NotFound, ValidationError

from apps.shop_app.models import (
    Category,
    Product,
    Sales,
    ProductImage,
    ProductAttributeValue,
    ProductComment,
    Order,
    OrderItem,
)


class ParentCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ("id", "name")


class ShopCategorySerializer(serializers.ModelSerializer):
    parent = ParentCategorySerializer(many=False, allow_null=True)
    category_image = serializers.URLField(
        source="category_image.image.url", allow_null=True
    )

    class Meta:
        model = Category
        exclude = ("is_active",)


class ProductImageSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = ProductImage
        fields = ("image", "order")

    @extend_schema_field(serializers.URLField())
    def get_image(self, obj):
        return obj.get_product_image_url


class RecommenderProductSerializer(serializers.ModelSerializer):
    product_image = serializers.SerializerMethodField(allow_null=True)

    class Meta:
        model = Product
        fields = (
            "id",
            "category_id",
            "product_name",
            "product_slug",
            "price",
            "new_price",
            "is_amazing",
            "product_image",
        )

    @extend_schema_field(serializers.URLField())
    def get_product_image(self, obj):
        img = obj.product_image.all()
        return img[0].get_product_image_url


class MostProductSaleSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source="product.id")
    product_slug = serializers.CharField(source="product.product_slug")
    product_name = serializers.CharField(source="product.product_name")
    price = serializers.CharField(source="product.price")
    new_price = serializers.CharField(source="product.new_price")
    product_image = serializers.SerializerMethodField(allow_null=True)

    class Meta:
        model = Sales
        fields = (
            "id",
            "product_name",
            "product_slug",
            "price",
            "new_price",
            "product_image",
        )

    @extend_schema_field(serializers.URLField())
    def get_product_image(self, obj):
        img = obj.product.product_image.all()
        return img[0].get_product_image_url


class MostProductDiscountSerializer(RecommenderProductSerializer):
    discount_amount = serializers.SerializerMethodField()

    class Meta(RecommenderProductSerializer.Meta):
        fields = (
            "id",
            "category_id",
            "product_name",
            "product_slug",
            "price",
            "new_price",
            "discount_amount",
            "product_image",
        )

    @extend_schema_field(serializers.DecimalField(max_digits=10, decimal_places=2))
    def get_discount_amount(self, obj):
        return obj.discount_amount


class ProductAttributeValueSerializer(serializers.ModelSerializer):
    attribute_name = serializers.CharField(
        source="attribute_value.attribute.attribute_name"
    )
    attribute_value = serializers.CharField(source="attribute_value.attribute_value")

    class Meta:
        model = ProductAttributeValue
        fields = (
            "attribute_name",
            "attribute_value",
        )


class DetailProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name")
    category_id = serializers.IntegerField(source="category.id")
    product_image = ProductImageSerializer(many=True)
    discount_amount = serializers.SerializerMethodField()
    product_attribute_values = ProductAttributeValueSerializer(many=True)

    class Meta:
        model = Product
        exclude = ("is_active", "sku")

    @extend_schema_field(serializers.DecimalField(max_digits=10, decimal_places=2))
    def get_discount_amount(self, obj):
        return obj.discount_amount


class ProductCommentSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    is_owner = serializers.SerializerMethodField()

    class Meta:
        model = ProductComment
        exclude = ("is_active",)
        read_only_fields = ("user", "product")

    def create(self, validated_data):
        user_id = self.context["request"].user.id
        product_id = self.context["product_id"]
        return ProductComment.objects.create(
            user_id=user_id, product_id=product_id, **validated_data
        )

    @extend_schema_field(serializers.BooleanField())
    def get_is_owner(self, obj):
        return obj.user_id == self.context["request"].user.id


class CreateOrderSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)


class CreateOrderBatchSerializer(serializers.Serializer):
    items = CreateOrderSerializer(many=True, min_length=1)

    def create(self, validated_data):
        items = validated_data.get("items", None)
        user_id = self.context["request"].user.id
        order = Order.objects.create(user_id=user_id)
        item_list = [
            OrderItem(
                product_id=i["product_id"], quantity=i["quantity"], order_id=order.pk
            )
            for i in items
        ]
        OrderItem.objects.bulk_create(item_list)
        return {"items": items}


class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.product_name", read_only=True)
    price = serializers.CharField(source="product.price")
    new_price = serializers.CharField(source="product.new_price")
    product_image = serializers.SerializerMethodField(allow_null=True)

    class Meta:
        model = OrderItem
        exclude = ("is_active", "created_at", "updated_at")

    @extend_schema_field(serializers.URLField())
    def get_product_image(self, obj):
        img = obj.product.product_image.all()
        return img[0].get_product_image_url if img else None


class OrderSerializer(serializers.ModelSerializer):
    order_items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        exclude = ("is_active",)
        read_only_fields = ("is_complete", "status", "user")


class AddOrderItemSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.only("id").filter(is_active=True)
    )
    quantity = serializers.IntegerField(min_value=1)

    class Meta:
        model = OrderItem
        fields = ("product", "quantity")

    def create(self, validated_data):
        order_id = self.context["order_id"]
        user_id = self.context["request"].user.id

        # check order dose exists
        order = Order.objects.filter(id=order_id, is_active=True, user_id=user_id).only(
            "id"
        )
        if not order.exists():
            raise NotFound("Order does not exist")
        else:
            # check product in order
            if OrderItem.objects.filter(
                order_id=order_id,
                product_id=validated_data["product"].id,
                is_active=True,
            ).exists():
                raise ValidationError("product already added is order")
            else:
                # create order
                return OrderItem.objects.create(
                    product_id=validated_data["product"].id,
                    quantity=validated_data["quantity"],
                    order_id=order_id,
                )
