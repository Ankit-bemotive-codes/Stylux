from django.contrib import admin
from django.utils.html import format_html

from core.models import Address, Category, Ecomm_OrderItem, Ecomm_order, Product


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "description")
    search_fields = ("name", "description")
    ordering = ("name",)
    list_per_page = 25


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "price", "image_preview", "is_featured", "is_active")
    list_filter = ("category", "is_featured", "is_active")
    search_fields = ("name", "description")
    list_editable = ("is_featured", "is_active")
    autocomplete_fields = ("category",)
    list_select_related = ("category",)
    readonly_fields = ("created_at", "image_preview")
    ordering = ("-is_featured", "-created_at", "name")
    list_per_page = 25
    fieldsets = (
        (None, {"fields": ("name", "category", "price", "image_url", "image_preview", "description")}),
        ("Storefront status", {"fields": ("is_featured", "is_active")}),
        ("Metadata", {"fields": ("created_at",)}),
    )
    actions = ("mark_active", "mark_inactive", "mark_featured", "mark_not_featured")

    @admin.display(description="Image")
    def image_preview(self, product):
        if not product.local_image_url:
            return "No local image"
        return format_html(
            '<img src="{}" alt="{}" style="width:48px;height:48px;object-fit:cover;border-radius:4px;">',
            product.local_image_url,
            product.name,
        )

    @admin.action(description="Mark selected products active")
    def mark_active(self, request, queryset):
        queryset.update(is_active=True)

    @admin.action(description="Mark selected products inactive")
    def mark_inactive(self, request, queryset):
        queryset.update(is_active=False)

    @admin.action(description="Mark selected products featured")
    def mark_featured(self, request, queryset):
        queryset.update(is_featured=True)

    @admin.action(description="Mark selected products not featured")
    def mark_not_featured(self, request, queryset):
        queryset.update(is_featured=False)

@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ("user", "address_line1", "city", "state", "country")
    list_filter = ("city", "state", "country")
    search_fields = ("address_line1", "address_line2", "city", "state", "country")
    ordering = ("city",)
    list_per_page = 20


@admin.register(Ecomm_order)
class EcommOrderAdmin(admin.ModelAdmin):
    list_display = ("order_id", "user", "total_amount", "payment_status", "order_placed_at")
    list_filter = ("payment_status", "payment_mode", "order_placed_at")
    search_fields = ("order_id", "user__username", "order_tracking_number", "razor_order_id")
    ordering = ("-order_placed_at",)
    list_per_page = 25


@admin.register(Ecomm_OrderItem)
class EcommOrderItemAdmin(admin.ModelAdmin):
    list_display = ("order", "product", "quantity")
    list_filter = ("order", "product")
    search_fields = ("order__order_id", "product__name")
    ordering = ("order", "product")
    list_per_page = 25