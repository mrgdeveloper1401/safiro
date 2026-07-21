from django.contrib import admin

from .models import (
    Category,
    Product,
    ProductImage,
    Attribute,
    AttributeValue,
    ProductAttributeValue,
    ProductComment,
    Order,
    OrderItem,
    Sales,
)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "parent_id",
        "slug",
        "category_image_id",
        "is_active",
        "created_at",
        "updated_at",
    )
    search_fields = ("name",)
    raw_id_fields = ("parent", "category_image")
    list_per_page = 30
    list_editable = ("is_active",)
    list_filter = ("is_active", "parent_id")


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "product_name",
        "category_id",
        "stock_number",
        "price",
        "new_price",
        "is_active",
        "is_amazing",
        "created_at",
        "updated_at",
    )
    list_editable = ("is_active", "stock_number", "price", "new_price", "is_amazing")
    list_filter = ("is_active", "created_at", "updated_at", "is_amazing")
    list_per_page = 30
    search_fields = ("product_name", "id")
    search_help_text = (
        "برای جست و جو میتوانید از نام محصول و شماره ایدی محصول استفاده کنید"
    )
    raw_id_fields = ("category",)
    list_display_links = ("id", "product_name")

    def get_queryset(self, request):
        return super().get_queryset(request).defer("description")


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display_links = ("id", "product_id", "image_id")
    raw_id_fields = ("product", "image")
    list_display = (
        "id",
        "product_id",
        "image_id",
        "order",
        "is_active",
        "created_at",
        "updated_at",
    )
    list_editable = ("is_active", "order")
    list_filter = ("is_active", "created_at", "updated_at")
    search_fields = ("product__id", "id")
    search_help_text = (
        "برای جست و جو میتوانید از شماره ایدی محصول و ایدی فیلد استفاده کنید"
    )
    list_per_page = 30


@admin.register(Attribute)
class AttributeAdmin(admin.ModelAdmin):
    list_display = ("id", "attribute_name", "is_active", "created_at", "updated_at")
    list_per_page = 30
    list_filter = ("is_active", "created_at", "updated_at")
    list_editable = ("is_active",)
    list_display_links = ("id", "attribute_name")


@admin.register(AttributeValue)
class AttributeValueAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "attribute_id",
        "attribute_value",
        "is_active",
        "created_at",
        "updated_at",
    )
    list_editable = ("is_active",)
    list_filter = ("is_active", "created_at", "updated_at")
    list_display_links = ("id", "attribute_id", "attribute_value")
    list_per_page = 30
    raw_id_fields = ("attribute",)


@admin.register(ProductAttributeValue)
class ProductAttributeValueAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "product_id",
        "attribute_value_id",
        "is_active",
        "created_at",
        "updated_at",
    )
    list_editable = ("is_active",)
    list_filter = ("is_active", "created_at", "updated_at")
    list_display_links = ("id", "attribute_value_id", "product_id")
    list_per_page = 30
    raw_id_fields = ("product", "attribute_value")


@admin.register(ProductComment)
class ProductCommentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "product_id",
        "user_id",
        "is_active",
        "created_at",
        "updated_at",
    )
    list_editable = ("is_active",)
    list_filter = ("is_active", "created_at", "updated_at")
    list_display_links = ("id", "id", "user_id", "product_id")
    list_per_page = 30
    raw_id_fields = ("product", "user")
    search_fields = ("product__id", "user__phone")
    search_help_text = (
        "برای جست و جو میتوانید از شماره موبایل کاربر یا ایدی محصول استفاده کنید"
    )


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user_id",
        "get_user_phone",
        "is_complete",
        "status",
        "is_active",
        "created_at",
        "updated_at",
    )
    list_filter = ("is_complete", "created_at", "updated_at", "is_active")
    search_fields = ("user__id", "user__phone")
    search_help_text = (
        "برای جست و جو میتوانید از ایدی کاربر یا شماره موبایل استفاده کنید"
    )
    list_per_page = 30
    raw_id_fields = ("user",)
    list_editable = ("is_complete", "is_active", "status")
    list_display_links = ("id", "user_id", "get_user_phone")

    def get_user_phone(self, obj):
        return obj.user.phone

    def get_queryset(self, request):
        fields = (
            "user__phone",
            "is_complete",
            "is_active",
            "created_at",
            "updated_at",
            "status",
        )
        return super().get_queryset(request).select_related("user").only(*fields)


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "product_id",
        "order_id",
        "quantity",
        "is_active",
        "created_at",
        "updated_at",
    )
    raw_id_fields = ("product", "order")
    list_filter = ("is_active", "created_at", "updated_at")
    list_editable = ("is_active",)
    list_display_links = ("id", "product_id", "order_id")
    list_per_page = 30


@admin.register(Sales)
class SalesAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user_id",
        "product_id",
        "get_user_phone",
        "quantity",
        "is_active",
        "created_at",
        "updated_at",
    )
    raw_id_fields = ("product", "user")
    list_per_page = 30
    list_filter = ("is_active", "created_at", "updated_at")
    list_editable = ("is_active", "quantity")
    search_fields = ("user__id", "user__phone", "product__id")
    search_help_text = "برای جست و جو میتوانید از ایدی کاربر یا محصول یا شماره موبایل کاربر استفاده کنید"
    list_display_links = ("id", "user_id", "product_id", "get_user_phone")
    list_select_related = ("user",)

    def get_user_phone(self, obj):
        return obj.user.phone

    def get_queryset(self, request):
        fields = (
            "user__phone",
            "product_id",
            "quantity",
            "is_active",
            "created_at",
            "updated_at",
        )
        return super().get_queryset(request).only(*fields)
