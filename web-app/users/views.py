from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import generic
from django.contrib.auth.decorators import login_required
from .forms import *
from django.contrib import messages
from .models import *
import os
from django.core.files import File




def home(request):
    initial_data()
    return render(request, 'index.html')


def initial_data():

    Warehouse.objects.all().delete()
    Product.objects.all().delete()
    
    warehouse1 = Warehouse(x=1, y=1)
    warehouse1.save()
    warehouse2 = Warehouse(x=2, y=2)
    warehouse2.save()

    # Create a new product linked to the warehouse
    product1 = Product(description="Basketball", quantity=200, warehouse=warehouse1, price=25)
    product2 = Product(description="Candy", quantity=100, warehouse=warehouse2, price=3)
    # from django.conf import settings
    
    # image_path = os.path.join('/code','users', 'product_image', 'basketball.jpeg')

    # # Check if the file exists before proceeding
    # if not os.path.exists(image_path):
    #     raise FileNotFoundError(f"No such file or directory: '{image_path}'")
    
    # # Attach the image to the Product instance
    # with open(image_path, 'rb') as img:
    #     product.image.save('basketball.jpeg', File(img), save=True) 
    
    product1.save()
    product2.save()

    print(f"Initialized!")

@login_required
def user_home(request):
    
    return render(request, 'user_home.html')


def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()

            user.email = form.cleaned_data.get('email')
            user.save()
            return redirect('login')  
    else:
        form = CustomUserCreationForm()
    return render(request, 'signup.html', {'form': form})

@login_required
def user_info(request):
    user = request.user

    context = {
        'user': user
    }
    return render(request, 'user_info.html', context)


@login_required
def update_user_info(request):
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        if user_form.is_valid():
            user_form.save()
            return redirect('user_info')

    else:
        user_form = UserUpdateForm(instance=request.user)

    context = {'user_form': user_form}
    return render(request, 'update_user_info.html', context)



@login_required
def shopping(request):    
    products = Product.objects.all()
    print(products)  
    wh = Warehouse.objects.all()
    print(wh)
    return render(request, 'shopping.html', {'products': products})

@login_required
def myorder(request):    
    return render(request, 'myorder.html')