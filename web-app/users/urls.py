from django.urls import path
from django.contrib.auth import views as auth_views
from . import views  
from .views import *
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [

    path('', home, name='home'),

    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='logout.html'), name='logout'),

    path('user-home/', user_home, name='user_home'), 

    path('signup/', signup, name='signup'),
    

    # path('register-driver/', register_driver, name='register_driver'),
    

    path('user-info/', user_info, name='user_info'),
    
    path('update-user-info/', update_user_info, name='update_user_info'),
    # path('update-driver-info/', update_driver_info, name='update_driver_info'),
    path('shopping/', shopping_view, name='shopping'), 
    path('submit-cart/', submit_cart, name='submit_cart'),
    path('view_-art-order/', view_cart_order, name='view_cart_order'),
    path('myorder/', myorder, name='myorder'), 
    path('order-confirmation/', order_confirmation, name='order_confirmation'), 
    

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

