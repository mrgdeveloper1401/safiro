from rest_framework import serializers

from apps.shop_app.models import Category, Product


class ParentCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ("id", "name")


class ShopCategorySerializer(serializers.ModelSerializer):
    parent = ParentCategorySerializer(many=False, allow_null=True)
    category_image = serializers.URLField(source="category_image.image.url", allow_null=True)

    class Meta:
        model = Category
        exclude = ('is_active',)


class IsAmazingProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = (
            "id",
            "category_id",
            "product_name",
            "product_slug",
            "price",
            "new_price",
            "is_amazing"
        )
