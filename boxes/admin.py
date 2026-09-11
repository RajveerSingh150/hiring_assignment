from django.contrib import admin

from .models import Box, Order, OrderItem, Product


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "length_cm", "width_cm", "height_cm", "weight_kg")


@admin.register(Box)
class BoxAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "internal_length_cm",
        "internal_width_cm",
        "internal_height_cm",
        "max_weight_kg",
        "cost",
    )


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "created_at")
    inlines = [OrderItemInline]
