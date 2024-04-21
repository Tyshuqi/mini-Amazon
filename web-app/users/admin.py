from django.contrib import admin
from .models import Warehouse, Product

# Register your models here.

class WarehouseAdmin(admin.ModelAdmin):
    list_display = ('x', 'y')  # Adjust fields to display as needed

class ProductAdmin(admin.ModelAdmin):
    list_display = ('description', 'quantity', 'warehouse')  # Adjust fields to display as needed
    list_filter = ('warehouse',)  # Add filters as needed
    search_fields = ('description',)  # Enable search functionality on description

admin.site.register(Warehouse, WarehouseAdmin)
admin.site.register(Product, ProductAdmin)
