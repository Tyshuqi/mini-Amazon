from django.db import migrations, models
import os
from django.core.files import File

def add_initial_data(apps, schema_editor):
    Warehouse = apps.get_model('users', 'Warehouse')
    Product = apps.get_model('users', 'Product')

    # Empty the Warehouse and Product tables
    Warehouse.objects.all().delete()
    Product.objects.all().delete()
    
    # Creating warehouse instances
    warehouse1 = Warehouse.objects.create(x=1, y=2)
    warehouse2 = Warehouse.objects.create(x=3, y=4)

    # Creating product instances
    Product.objects.create(description='Product A', quantity=150, warehouse=warehouse1)
    #Product.objects.create(description='Product B', quantity=90, warehouse=warehouse2)

    # Path to the image
    image_path = os.path.join(os.path.dirname(__file__), '..', 'product_image', 'basketball.jpeg')

    # Ensure the image file exists
    if os.path.exists(image_path):
        # Create product instance
        product = Product(
            description='Basketball',
            quantity=100,
            warehouse=warehouse1
        )
        # Open the image file, and save it to the ImageField
        with open(image_path, 'rb') as image_file:
            product.image.save('product_image.jpg', File(image_file), save=True)




class Migration(migrations.Migration):
    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(add_initial_data),
    ]
