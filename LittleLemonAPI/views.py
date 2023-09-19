from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.models import User, Group
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status, generics
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .models import MenuItem, Category
from .serializers import MenuItemSerializer, CategorySerializer, ManagerListSerializer


class MenuItems(generics.ListCreateAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer

    def get_permissions(self):
        if self.request.method != 'GET':
            self.permission_classes = [IsAuthenticated, IsAdminUser]
        return super(MenuItems, self).get_permissions()


class CategoryView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminUser]


class MenuItemView(generics.RetrieveUpdateDestroyAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer

    def get_permissions(self):
        permission_classes = [IsAuthenticated]
        if self.request.method == 'PATCH':
            permission_classes = [IsAuthenticated, IsAdminUser]
        if self.request.method == 'DELETE':
            permission_classes = [IsAuthenticated, IsAdminUser]
        return[permission() for permission in permission_classes]
    
    
class ManagerListView(generics.ListCreateAPIView):
    queryset = User.objects.filter(groups__name='Manager')
    serializer_class = ManagerListSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        username = request.data['username']
        if username:
            user = get_object_or_404(User, username=username)
            managers = Group.objects.get(name='Manager')
            managers.user_set.add(user)
            return JsonResponse(status=201, data={'message':'User added to Managers group'}) 

class ManagerDeleteView(generics.DestroyAPIView):
    queryset = User.objects.filter(groups__name='Manager')
    serializer_class = ManagerListSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def delete(self, request, *args, **kwargs):
        pk = self.kwargs['pk']
        user = get_object_or_404(User, pk=pk)
        managers = Group.objects.get(name='Manager')
        managers.user_set.remove(user)
        return JsonResponse(status=200, data={'message': 'User is removed from Manager group'})
    
class DeliveryCrewListView(generics.ListCreateAPIView):
    queryset = User.objects.filter(groups__name='Delivery Crew')
    serializer_class = ManagerListSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def post(self, request):
        username = request.data['username']
        if username:
            user = get_object_or_404(User, username=username)
            delivery_crew = Group.objects.get(name='Delivery Crew')
            delivery_crew.user_set.add(user)
            return JsonResponse(status=201, data={'message': 'User added to Delivery Crew group'})
        
class DeliveryCrewDeleteView(generics.DestroyAPIView):
    queryset = User.objects.filter(groups__name='Delivery Crew')
    serializer_class = ManagerListSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def delete(self, request, *args, **kwargs):
        pk = self.kwargs['pk']
        user = get_object_or_404(User, pk=pk)
        delivery_crew = Group.objects.get(name='Delivery Crew')
        delivery_crew.user_set.remove(user)
        return JsonResponse(status=200, data={'message': 'User is removed from Delivery Crew group'})
        
    
    

    
# admin = dbcd5c252275d41c4baa5759523c7fed081c983d
# janedoe = b5181c578adb5d3b89e49764cfa1885f45ae252b