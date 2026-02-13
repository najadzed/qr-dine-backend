from django.urls import path
from .views import *

urlpatterns = [
    path("menu/", menu_list),
    path("order/", create_order),              # POST order
    path("orders/", all_orders),               # GET all orders ✅
    path("order/update-status/", update_status),
    path("order/delete/<int:order_id>/", delete_order),
    path("login/", login_user),
    path("restaurants/", restaurants_list),
    path("tables/", tables_list),
    path("categories/", categories_list),
    path("menu/<int:pk>/", menu_detail),

]
