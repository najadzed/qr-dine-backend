from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import *
from .serializers import *
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.db import transaction
from django.contrib.auth import authenticate
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes

from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.decorators import parser_classes
from rest_framework import status



@api_view(["POST"])
def login_user(request):
    username = request.data.get("username")
    password = request.data.get("password")

    user = authenticate(username=username, password=password)

    if not user:
        return Response({"error": "Invalid credentials"}, status=400)

    profile = UserProfile.objects.get(user=user)

    refresh = RefreshToken.for_user(user)

    return Response({
        "access": str(refresh.access_token),
        "refresh": str(refresh),
        "role": profile.role,
        "restaurant_id": profile.restaurant.id,
        "restaurant_name": profile.restaurant.name,
    })


# Get Menu


@api_view(["GET", "POST"])
@parser_classes([MultiPartParser, FormParser])
def menu_list(request):

    # 🔹 GET ALL MENU ITEMS
    if request.method == "GET":
        items = MenuItem.objects.all()
        serializer = MenuItemSerializer(
            items,
            many=True,
            context={"request": request}
        )
        return Response(serializer.data)

    # 🔹 CREATE NEW MENU ITEM
    if request.method == "POST":
        serializer = MenuItemSerializer(
            data=request.data,
            context={"request": request}
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=400)


# Create Order (Customer)

@api_view(["POST"])
def create_order(request):
    table_id = request.data.get("table")
    items = request.data.get("items")  # [{id:1, qty:2}, ...]

    if not table_id or not items:
        return Response({"error": "Table and items required"}, status=400)

    try:
        table = Table.objects.get(id=table_id)
    except Table.DoesNotExist:
        return Response({"error": "Table not found"}, status=404)

    # 🔒 Atomic transaction
    with transaction.atomic():
        order = Order.objects.create(table=table)

        for i in items:
            item_id = i.get("id") or i.get("item") or i.get("item_id")
            quantity = i.get("qty") or i.get("quantity")

            if not item_id or not quantity:
                return Response(
                    {"error": "Invalid item format"},
                    status=400
                )

            try:
                menu_item = MenuItem.objects.get(id=item_id)
            except MenuItem.DoesNotExist:
                return Response(
                    {"error": f"Menu item {item_id} not found"},
                    status=404
                )

            OrderItem.objects.create(
                order=order,
                item=menu_item,
                quantity=quantity
            )



    # 🔔 WebSocket notify kitchen AFTER success
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "orders",
        {
            "type": "order_update",
            "data": {
                "event": "new_order",
                "order_id": order.id,
                "table_number": table.table_number,   # ✅ correct field
            }
        }
    )

    return Response({"message": "Order created", "order_id": order.id})


# Kitchen: Get all orders
@permission_classes([IsAuthenticated])
@api_view(["GET"])
def all_orders(request):
    orders = Order.objects.all().order_by("-created_at")
    serializer = OrderSerializer(
        orders,
        many=True,
        context={"request": request}
    )
    return Response(serializer.data)


# Update Order Status (Kitchen Buttons)
@permission_classes([IsAuthenticated])
@api_view(["POST"])
def update_status(request):
    order_id = request.data.get("order_id")
    status = request.data.get("status")

    order = Order.objects.get(id=order_id)
    order.status = status
    order.save()

    return Response({"message": "Status updated"})

@permission_classes([IsAuthenticated])
@api_view(["DELETE"])
def delete_order(request, order_id):
    try:
        order = Order.objects.get(id=order_id)
        order.delete()
        return Response({"message": "Order deleted"})
    except Order.DoesNotExist:
        return Response({"error": "Order not found"}, status=404)
    
@permission_classes([IsAuthenticated])
@api_view(["GET", "POST"])
def restaurants_list(request):
    if request.method == "GET":
        data = Restaurant.objects.all()
        return Response(RestaurantSerializer(data, many=True).data)

    if request.method == "POST":
        serializer = RestaurantSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

@permission_classes([IsAuthenticated])
@api_view(["GET", "POST"])
def tables_list(request):
    if request.method == "GET":
        data = Table.objects.all()
        return Response(TableSerializer(data, many=True).data)

    if request.method == "POST":
        serializer = TableSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

@permission_classes([IsAuthenticated])
@api_view(["GET", "POST"])
def categories_list(request):
    if request.method == "GET":
        data = MenuCategory.objects.all()
        return Response(CategorySerializer(data, many=True).data)

    if request.method == "POST":
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        
from django.shortcuts import get_object_or_404

@api_view(["DELETE"])
def menu_detail(request, pk):
    item = get_object_or_404(MenuItem, pk=pk)
    item.delete()
    return Response({"message": "Item deleted"})
