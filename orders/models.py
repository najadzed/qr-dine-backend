from django.db import models
from django.utils import timezone
from django.db.models import Max
from django.contrib.auth.models import User

class Restaurant(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class UserProfile(models.Model):
    ROLE_CHOICES = (
        ("owner", "Owner"),
        ("kitchen", "Kitchen"),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)


# Restaurant (for future multi-restaurant support)


# Tables in restaurant
class Table(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    table_number = models.IntegerField()

    def __str__(self):
        return f"{self.restaurant.name} - Table {self.table_number}"


# Menu Categories (Starters, Drinks, Main Course)
class MenuCategory(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


# Menu Items with Image
class MenuItem(models.Model):
    category = models.ForeignKey(MenuCategory, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    image = models.ImageField(upload_to="menu_images/", null=True, blank=True)
    available = models.BooleanField(default=True)

    def __str__(self):
        return self.name


# Customer Orders
class Order(models.Model):
    STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("Preparing", "Preparing"),
        ("Ready", "Ready"),
        ("Served", "Served"),
    ]

    table = models.ForeignKey(Table, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Pending")
    created_at = models.DateTimeField(auto_now_add=True)

    # ✅ NEW FIELD (daily token number)
    daily_number = models.IntegerField(default=0)

    def save(self, *args, **kwargs):
        # Only when creating new order
        if not self.pk:
            today = timezone.now().date()

            last_number = (
                Order.objects.filter(created_at__date=today)
                .aggregate(Max("daily_number"))["daily_number__max"]
            )

            self.daily_number = (last_number or 0) + 1

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Order #{self.daily_number} - Table {self.table.table_number}"

    @property
    def total_price(self):
        return sum(item.item.price * item.quantity for item in self.items.all())
    
# Items inside an order (cart)
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.item.name} x {self.quantity}"
