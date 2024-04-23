from django.db import models
from django.contrib.auth.models import User


class Warehouse(models.Model):
    x = models.IntegerField()
    y = models.IntegerField()

    def __str__(self):
        return f"Warehouse at ({self.x}, {self.y})"



class Product(models.Model):
    description = models.TextField()
    quantity = models.IntegerField(default=0)
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name='products')
    price = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    image = models.ImageField(upload_to='images/', null=True, blank=True)

    def __str__(self):
        return self.description

class Order(models.Model):
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('error', 'Error'), 
        ('packing', 'Packing'),
        ('packed', 'Packed'), 
        ('loading', 'Loading'), 
        ('loaded', 'Loaded'), 
        ('delivering', 'Delivering'), 
        ('delivered', 'Delivered')
    ], default='pending')
    des_x = models.IntegerField(null=True, blank=True)
    des_y = models.IntegerField(null=True, blank=True)
    upsUsername = models.CharField(max_length=100, null=True, blank=True)
    upsUserID =  models.IntegerField(null=True, blank=True)

    def __str__(self):
       
        return f"{self.quantity} x {self.product.description} for Order {self.order.id} (UPS Username: {self.upsUsername})"
    
class CartOrder(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_open = models.BooleanField(default=True)
    des_x = models.IntegerField(null=True, blank=True)
    des_y = models.IntegerField(null=True, blank=True)
    ups_name = models.CharField(max_length=100, null=True, blank=True) 


class OrderItem(models.Model):
    order_id = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items', null=True, blank=True)
    cart_order = models.ForeignKey(CartOrder, on_delete=models.CASCADE , null=True, related_name='cart_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    status = models.CharField(max_length=20, choices=[
        ('enough', 'Enough'), 
        ('short', 'Short')
    ], default='enough')
    

    def __str__(self):
        #return f"{self.quantity} x {self.product.description} for Order {self.order_id.id}"
        return f"{self.quantity} x {self.product.description}"





