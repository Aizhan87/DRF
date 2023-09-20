from rest_framework import serializers, generics
from .models import MenuItem
from .models import Category, Cart, Order, OrderItem
from decimal import Decimal
from django.contrib.auth.models import User


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'slug', 'title']


class MenuItemSerializer(serializers.ModelSerializer):
    category_id = serializers.IntegerField(write_only=True)
    category = CategorySerializer(read_only=True)

    class Meta:
        model = MenuItem
        fields = ['id', 'title', 'price', 'featured', 'category', 'category_id']

class ManagerListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','username','email']

class CartSerializer(serializers.ModelSerializer):
    menuitem = MenuItemSerializer
    class Meta:
        model = Cart
        fields = ['menuitem','quantity', 'price', 'unit_price']
        extra_kwargs = {
            'quantity': {'min_value': 1},
        }

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username']

class OrderSerializer(serializers.ModelSerializer):
    user = UserSerializer
    class Meta:
        model = Order
        fields = ['id','user','total','status','delivery_crew','date']
        
class SingleOrderSerializer(serializers.ModelSerializer):
    menuitem = MenuItem
    class Meta:
        model = OrderItem
        fields = ['menuitem','quantity']