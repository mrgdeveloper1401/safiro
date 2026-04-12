from rest_framework import serializers

from apps.shop_app.models import Category


class ParentCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ("id", "name")


class ShopCategorySerializer(serializers.ModelSerializer):
    parent = ParentCategorySerializer(many=False, allow_null=True)

    class Meta:
        model = Category
        exclude = ('is_active',)
