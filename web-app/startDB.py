import os
import django

# Specify the settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'finalproj.settings')
django.setup()
from users.models import *
import os
from django.core.files import File

Warehouse.objects.all().delete()
Product.objects.all().delete()
    
warehouse1 = Warehouse(x=1, y=1)
warehouse1.save()
warehouse2 = Warehouse(x=2, y=2)
warehouse2.save()

# Create a new product linked to the warehouse
product1 = Product(description="Basketball", quantity=200, warehouse=warehouse1, price=25)
product2 = Product(description="Duke Mocha Bear", quantity=100, warehouse=warehouse2, price=13)
from django.conf import settings
    
image_path1 = os.path.join('/code','users', 'product_image', 'basketball.jpeg')
# Check if the file exists before proceeding
if not os.path.exists(image_path1):
    raise FileNotFoundError(f"No such file or directory: '{image_path}'")    
# Attach the image to the Product instance
with open(image_path1, 'rb') as img:
    product1.image.save('basketball.jpeg', File(img), save=True) 

image_path2 = os.path.join('/code','users', 'product_image', 'duke_mocha_bear.jpeg')
# Check if the file exists before proceeding
if not os.path.exists(image_path2):
    raise FileNotFoundError(f"No such file or directory: '{image_path}'")    
# Attach the image to the Product instance
with open(image_path2, 'rb') as img:
    product2.image.save('duke_mocha_bear.jpeg', File(img), save=True) 
    
product1.save()
product2.save()

print(f"Initialized DB!")