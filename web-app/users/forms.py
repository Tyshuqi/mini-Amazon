from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import *


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('email',)



class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email']

class DestinationForm(forms.ModelForm):
    class Meta:
        model = CartOrder
        fields = ['des_x', 'des_y', 'ups_name']
        
        
class UpdateOrderForm(forms.Form):
    order_id = forms.IntegerField(widget=forms.HiddenInput())
    upsUsername = forms.CharField(label='Update UPS Username', max_length=100)      
