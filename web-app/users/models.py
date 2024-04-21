from django.db import models

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
    #image = models.ImageField(upload_to='images/')

    def __str__(self):
        return self.description

class Order(models.Model):
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'), 
        ('packing', 'Packing'),
        ('packed', 'Packed'), 
        ('loading', 'Loading'), 
        ('loaded', 'Loaded'), 
        ('delivering', 'Delivering'), 
        ('delivered', 'Delivered')
    ], default='pending')
    des_x = models.IntegerField()
    des_y = models.IntegerField()
    upsUsername = models.CharField(max_length=100)  # Added field for UPS Username

    def __str__(self):
        return f"{self.quantity} x {self.product.description} for Order {self.order.id} (UPS Username: {self.upsUsername})"
    


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()

    def __str__(self):
        return f"{self.quantity} x {self.product.description} for Order {self.order.id}"
