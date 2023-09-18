from rest_framework import serializers, generics
from .models import MenuItem
from .models import Category
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
        fields = ['id', 'title', 'price',
                  'featured', 'category', 'category_id']

class ManagerListSerializer(serializers.ModelSerializer):
    class Meta():
        model = User
        fields = ['id','username','email']