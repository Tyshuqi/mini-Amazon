from django.db import models

class Warehouse(models.Model):
    #warehouse_id = models.AutoField(primary_key=True)
    x = models.IntegerField()
    y = models.IntegerField()

    def __str__(self):
        return f"Warehouse at ({self.x}, {self.y})"

class Product(models.Model):
    # product_id = models.CharField(max_length=50, unique=True)
    description = models.TextField()
    quantity = models.IntegerField(default=0)  # Adjusted for total stock tracking
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name='products')

    def __str__(self):
        return self.description

class Order(models.Model):
    #order_id = models.AutoField(primary_key=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    #warehouse = models.ForeignKey(Warehouse, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'), 
        ('packing', 'Packing'),
        ('packed', 'Packed'), 
        ('loading', 'Loading'), 
        ('loaded', 'Loaded'), 
        ('delivering', 'Delivering'), 
        ('delivered', 'Delivered')
    ], default='pending')
    address = models.CharField(max_length=100)

    def __str__(self):
        return f"Order {self.id} for {self.product.description}"

