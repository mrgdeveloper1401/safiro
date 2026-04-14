from django.db import models

from apps.auth_app.models import User
from apps.core_app.models import ActiveMixin, ModifyMixin, Image


class Category(ActiveMixin, ModifyMixin):
    name = models.CharField(max_length=50, unique=True)
    parent = models.ForeignKey("self", on_delete=models.PROTECT, null=True, blank=True)
    slug = models.SlugField(max_length=255, unique=True, allow_unicode=True)
    category_image = models.ForeignKey(Image, on_delete=models.PROTECT, null=True, blank=True)

    class Meta:
        db_table = "category"


class Product(ActiveMixin, ModifyMixin):
    category = models.ForeignKey(Category, on_delete=models.PROTECT)
    product_name = models.CharField(max_length=255, db_index=True)
    product_slug = models.SlugField(max_length=255, allow_unicode=True)
    stock_number = models.PositiveIntegerField(default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    new_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    sku = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    is_amazing = models.BooleanField(default=False)

    class Meta:
        db_table = "product"


class ProductImage(ModifyMixin, ActiveMixin):
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="product_image")
    image = models.ForeignKey(Image, on_delete=models.PROTECT, related_name="image_product")
    order = models.PositiveIntegerField(default=1)

    class Meta:
        db_table = "product_image"

    @property
    def get_product_image_url(self):
        return self.image.get_image_url


class Attribute(ModifyMixin, ActiveMixin):
    attribute_name = models.CharField(max_length=255)

    class Meta:
        db_table = "attribute"


class AttributeValue(ModifyMixin, ActiveMixin):
    attribute = models.ForeignKey(Attribute, on_delete=models.PROTECT)
    attribute_value = models.CharField(max_length=255)

    class Meta:
        db_table = "attribute_value"


class ProductAttributeValue(ModifyMixin, ActiveMixin):
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="product_attribute_values")
    attribute_value = models.ForeignKey(AttributeValue, on_delete=models.PROTECT)

    class Meta:
        db_table = "product_attribute_value"


class ProductComment(ModifyMixin, ActiveMixin):
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    comment = models.TextField()

    class Meta:
        db_table = "product_comment"


class Order(ModifyMixin, ActiveMixin):
    ORDER_STATUS = (
        ("pending", "Pending"),
        ("success", "Successful"),
        ("error", "Error"),
    )
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    is_complete = models.BooleanField(default=False)
    status = models.CharField(max_length=10, default="pending", choices=ORDER_STATUS)

    class Meta:
        db_table = "order"


class OrderItem(ModifyMixin, ActiveMixin):
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    order = models.ForeignKey(Order, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        db_table = "order_item"


class Sales(ModifyMixin, ActiveMixin):
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        db_table = "sales"
