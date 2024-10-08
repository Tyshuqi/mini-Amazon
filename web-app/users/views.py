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
from django.shortcuts import get_object_or_404
from django.shortcuts import get_list_or_404
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.views import LoginView
from .mysocket import *
from . import web_backend_pb2 as web
import time
from collections import defaultdict
from django.db import transaction
from mailjet_rest import Client
from django.contrib.auth.views import LoginView
from django.utils.http import url_has_allowed_host_and_scheme
from django.shortcuts import redirect
while True:
    try:
        print("Try to connect to backend...")
        #back_fd = clientSocket("vcm-38181.vm.duke.edu", 45678)
        back_fd = clientSocket("vcm-38127.vm.duke.edu", 45678)
        print("Success connected to backend! back_fd: ", back_fd)
        break
    except:
        time.sleep(0.5)
        continue
#     res = receiveResponse(back_fd, web.BResponse)        
#     # remove ack from ack_list
#     for ack in res.acks:
#         ack_list.remove_ack(ack)
class CustomLoginView(LoginView):
    template_name = 'login.html'

    def form_valid(self, form):
        # Regenerate session ID to prevent session fixation
        self.request.session.cycle_key()
        redirect_to = 'user_home/'
        
        return super().form_valid(form)

def home(request):
    
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
def myorder(request):    
    return render(request, 'myorder.html')

@login_required
def shopping_view(request):
    return render(request, 'shopping.html')


@login_required
def submit_cart(request):
    #CartOrder.objects.all().delete()
    #print(CartOrder.objects.all())
    if request.method == 'POST':
        CartOrder.objects.filter(user=request.user, is_open=True).update(is_open=False)
        # Get or create a new cart order
        cart_order, created = CartOrder.objects.get_or_create(user=request.user, is_open=True)
        
        for key in request.POST:
            if key.startswith('quantity_'):
                product_id = key.split('_')[1]
                quantity = int(request.POST[key])
                if quantity > 0:
                    product = Product.objects.get(id=product_id)
                    OrderItem.objects.create(cart_order=cart_order, product=product, quantity=quantity)

        # if  no longer allow additions
        #cart_order.is_open = False
        cart_order.save()

        return redirect('view_cart_order') 

    return render(request, 'shopping.html', {'products': Product.objects.all()})

@login_required
def view_cart_order(request):
    #print(CartOrder.objects.all())
    cart_order = get_object_or_404(CartOrder, user=request.user, is_open=True)
    if request.method == 'POST':
        form = DestinationForm(request.POST, instance=cart_order)
        if form.is_valid():
            form.save()
            return redirect('order_confirmation')  
    else:
        form = DestinationForm(instance=cart_order)
    
    order_items = OrderItem.objects.filter(cart_order=cart_order)
    return render(request, 'cart_order.html', {
        'order_items': order_items,
        'form': form
    })

@login_required
def order_confirmation(request):
    sessionid = request.COOKIES.get('sessionid')
    cart_order = get_object_or_404(CartOrder, cookie=sessionid, user=request.user, is_open=True)
    order_items = OrderItem.objects.filter(cart_order=cart_order)
    print("order_confirm", cart_order.des_x, cart_order.des_y, cart_order.ups_name)
    warehouse_groups = defaultdict(list)
    enough_items = defaultdict(list)
    short_items = []

    for item in order_items:
        if item.quantity <= item.product.quantity:
            item.status = 'enough'
            warehouse_groups[item.product.warehouse_id].append(item)
            item.save()
        else:
            item.status = 'short'
            item.save()
            short_items.append(item)
            reqq_msg = web.WCommands()
            more_msg = reqq_msg.askmore.add()
            more_msg.productid = item.product.id
            more_msg.count = item.quantity - item.product.quantity
            seqNum = ack_list.add_request()  
            more_msg.seqnum = seqNum

            sendRequest(back_fd, reqq_msg)
            print("Send askmore request!")
        

    # Create an Order for each group of items from the same warehouse where all items are 'enough'
    with transaction.atomic():  # Use a transaction to ensure data integrity
        for warehouse_id, items in warehouse_groups.items():
            if all(item.status == 'enough' for item in items):
                new_order = Order(
                    user = request.user,
                    status='pending',
                    des_x=cart_order.des_x,
                    des_y=cart_order.des_y,
                    upsUsername=cart_order.ups_name
                )
                new_order.save()
                for item in items:
                    item.order_id = new_order
                    item.save()
                enough_items[new_order.id] = items
                print("new_order.id: ", new_order.id, new_order.des_x, new_order.des_y, new_order.upsUsername)

                req_msg = web.WCommands()
                buy_msg = req_msg.buy.add()
                buy_msg.orderid = new_order.id
                seqNum = ack_list.add_request()  
                buy_msg.seqnum = seqNum

                sendRequest(back_fd, req_msg)
                print("Send buy request!")
                print(request.user)
                print(request.user.email)
                sendEmail("yxs0327@gmail.com", "Admin", str(request.user.email), request.user.username)
                print("Send email!")
                
    enough_items = dict(enough_items) 
    print("enough_items", enough_items)
    print("short_items", short_items)
    return render(request, 'order_confirmation.html', {
        'short_items': short_items,
        'enough_items': enough_items,
        'cart_order': cart_order
    })


def my_order_view(request):
    orders = Order.objects.filter(user=request.user)  

    
    if request.method == 'POST':
        form = UpdateOrderForm(request.POST)
        if form.is_valid():
            order_id = form.cleaned_data['order_id']
            upsUsername = form.cleaned_data['upsUsername']
            order = Order.objects.get(id=order_id)
            order.upsUsername = upsUsername
            order.save()

            req_msg = web.WCommands()
            buy_msg = req_msg.buy.add()
            buy_msg.orderid = order_id
            seqNum = ack_list.add_request()  
            buy_msg.seqnum = seqNum

            sendRequest(back_fd, req_msg)
            print("Send buy request!(after revise username)")
            return redirect('user_home') 
    else:
        form = UpdateOrderForm()

    return render(request, 'myorder.html', {'orders': orders, 'form': form})

def sendEmail(adminEmail, adminName, userEmail, userName):
    api_key = '2b3c16d686e729b76eeacb6ce417b7b1'
    api_secret = '6c4b3e2da82b3ffb2d3252fd8742ecda'
    mailjet = Client(auth=(api_key, api_secret), version='v3.1')
    data = {
    'Messages': [
        {
        "From": {
            "Email": adminEmail,
            "Name": adminName,
        },
        "To": [
            {
            "Email": userEmail,
            "Name": userName,
            }
        ],
        "Subject": "MiniAmazon Order Confirmation",
        "TextPart": "Your order has beedn successfully placed!",
        "CustomID": "AppGettingStartedTest"
        }
    ]
    }
    result = mailjet.send.create(data=data)
    print(result.status_code)
    print(result.json())    
    
def search_products(request):
    query = request.GET.get('search_input')
    products = Product.objects.all()
    if query:
        products = Product.objects.filter(description__icontains=query)

    return render(request, 'shopping.html', {'products': products})

def add_cart(request):
    # Close all existing open cart orders for the user
    # print(request.COOKIES)
    sessionid = request.COOKIES.get('sessionid')

    # CartOrder.objects.filter(user=request.user, is_open=True).update(is_open=False)
    # Get or create a new cart order that is open
    cart_order, created = CartOrder.objects.get_or_create(cookie=sessionid, user=request.user, is_open=True)
    product_id = request.POST.get('product_id')
    quantity = int(request.POST.get('quantity', 0))
    # for key in request.POST:
    #     if key.startswith('quantity_'):
    #         product_id = key.split('_')[1]
    #         quantity = int(request.POST[key])
    print("quantity, ", quantity, product_id)
    if quantity > 0:
        product = Product.objects.get(id=product_id)
        OrderItem.objects.create(cart_order=cart_order, product=product, quantity=quantity)
            # order_item.save()
    
    cart_order.save()
    # Optionally, redirect to a confirmation page or back to the cart to review
    return render(request, 'shopping.html', {'products': Product.objects.all()})

  

def review_cart(request):
    session_id = request.COOKIES.get('sessionid')
    # Get cart orders that were created or updated in the last 5 minutes
    cart_orders = get_list_or_404(CartOrder, user=request.user, cookie=session_id)
    print("Review session:", session_id, cart_orders)
    cart_order = cart_orders[-1]
    if request.method == 'POST':
        form = DestinationForm(request.POST, instance=cart_order)
        if form.is_valid():
            form.save()
            return redirect('order_confirmation')  
    else:
        form = DestinationForm(instance=cart_order)

    # Collect all order items from all cart orders
    order_items = []
    for cart_order in cart_orders:
        items = OrderItem.objects.filter(cart_order=cart_order)
        order_items.extend(items)
        print("Items in cart:", items)

    return render(request, 'cart_order.html', {
        'order_items': order_items,
        'form': form  # Consider handling multiple forms if necessary
    })