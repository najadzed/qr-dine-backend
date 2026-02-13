from django.contrib import admin
from .models import *


# Restaurant Admin
@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)


# Table Admin
@admin.register(Table)
class TableAdmin(admin.ModelAdmin):
    list_display = ("id", "restaurant", "table_number")
    list_filter = ("restaurant",)
    search_fields = ("table_number",)


# Menu Category Admin
@admin.register(MenuCategory)
class MenuCategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)


# Menu Item Admin (with image preview)
@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "category", "price", "available")
    list_filter = ("category", "available")
    search_fields = ("name",)
    readonly_fields = ("image_preview",)

    def image_preview(self, obj):
        if obj.image:
            return f'<img src="{obj.image.url}" width="80"/>'
        return "No Image"

    image_preview.allow_tags = True
    image_preview.short_description = "Image Preview"


# Inline Order Items in Order Page
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


# Order Admin (Kitchen Friendly)
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "table", "status", "created_at", "total_price")
    list_filter = ("status", "table")
    search_fields = ("id",)
    inlines = [OrderItemInline]


# Order Item Admin (optional separate view)
@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ("id", "order", "item", "quantity")
    search_fields = ("order__id", "item__name")
