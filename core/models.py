import uuid
from pathlib import Path

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.utils.text import slugify


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True, null=True)
    image = models.ImageField(upload_to="Media/", blank=True, null=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "core_category_choices"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


CATEGORY_CHOICES = Category


class Product(models.Model):
    name = models.CharField(max_length=160)
    category = models.ForeignKey(Category, related_name="products", on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    image_url = models.ImageField(upload_to="Media/", blank=True, null=True)
    description = models.TextField(blank=True)
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-is_featured", "-created_at", "name")

    @property
    def local_image_url(self):
        if not self.image_url or not self.image_url.name:
            return ""

        media_root = Path(settings.MEDIA_ROOT).resolve()
        try:
            image_path = Path(self.image_url.path).resolve()
            image_path.relative_to(media_root)
        except (ValueError, OSError):
            return ""

        return self.image_url.url if image_path.is_file() else ""

    def __str__(self):
        return self.name

"""Address table for a user."""
class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="addresses")
    address_line1 = models.CharField(max_length=255)
    address_line2 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "core_user_addresses"
        verbose_name_plural = "Addresses"

    def __str__(self):
        return f"{self.user}, {self.state}, {self.country}"


class Ecomm_order(models.Model):
    payment_mode_choices = (
        ("cod", "Cash on Delivery"),
        ("online", "Online payment"),
    )
    payment_status_choices = (
        ("pending", "Pending"),
        ("completed", "Completed"),
        ("failed", "Failed"),
    )

    order_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    shipping_address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, blank=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_mode = models.CharField(max_length=20, choices=payment_mode_choices, default="cod")
    payment_status = models.CharField(max_length=20, choices=payment_status_choices, default="pending")
    order_tracking_number = models.CharField(max_length=100, null=True, blank=True)
    order_placed_at = models.DateTimeField(auto_now_add=True)
    razor_order_id = models.CharField(max_length=250, null=True, blank=True)
    razor_payment_id = models.CharField(max_length=250, blank=True, null=True)
    razorpay_signature = models.CharField(max_length=250, null=True, blank=True)

    def __str__(self):
        return f"{self.user} -> {self.order_id}"


class Ecomm_OrderItem(models.Model):
    order = models.ForeignKey(Ecomm_order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()

    class Meta:
        db_table = "core_order_items"
        verbose_name_plural = "Order Items"

    def __str__(self):
        return f"{self.product.name} -> {self.order.order_id}"

    
