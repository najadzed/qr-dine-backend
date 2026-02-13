from rest_framework import serializers
from .models import *


class MenuItemSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(required=False)
    category_name = serializers.CharField(
        source="category.name",
        read_only=True
    )

    class Meta:
        model = MenuItem
        fields = [
            "id",
            "name",
            "price",
            "image",
            "available",
            "category",
            "category_name",
        ]



class OrderItemSerializer(serializers.ModelSerializer):
    item = MenuItemSerializer()
    item_name = serializers.CharField(source="item.name")

    class Meta:
        model = OrderItem
        fields = ["item", "quantity","item_name"]


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    total_price = serializers.ReadOnlyField()
    table_number = serializers.IntegerField(source="table.table_number")



    class Meta:
        model = Order
        fields = "__all__"

class RestaurantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Restaurant
        fields = "__all__"


class TableSerializer(serializers.ModelSerializer):
    restaurant_name = serializers.CharField(source="restaurant.name", read_only=True)

    class Meta:
        model = Table
        fields = ["id", "table_number", "restaurant", "restaurant_name"]

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuCategory
        fields = "__all__"  