from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.models import User, Group
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status, generics
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .models import MenuItem, Category, Cart
from .serializers import MenuItemSerializer, CategorySerializer, ManagerListSerializer, CartSerializer


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
        return [permission() for permission in permission_classes]


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
            return JsonResponse(status=201, data={'message': 'User added to Managers group'})


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


# class CartListView(generics.ListCreateAPIView):
#     serializer_class = CartSerializer
#     permission_classes = [IsAuthenticated]

#     def get_queryset(self):
#         queryset = Cart.objects.filter(user=self.request.user)
#         return queryset

#     def post(self, request, *arg, **kwargs):
#         serialized_item = CartAddSerializer(data=request.data)
#         serialized_item.is_valid(raise_exception=True)
#         id = request.data['menuitem']
#         quantity = request.data['quantity']
#         item = get_object_or_404(MenuItem, id=id)
#         price = int(quantity) * item.price
#         try:
#             Cart.objects.create(user=request.user, quantity=quantity, unit_price=item.price, price=price, menuitem_id=id)
#         except:
#             return JsonResponse(status=409, data={'This item is already in the cart'})
#         return JsonResponse(status=201, data={'message': 'item added to the cart'})

class CartListView(generics.ListCreateAPIView):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)

    def delete(self, request, *args, **kwargs):
        Cart.objects.all().filter(user=self.request.user).delete()
        return Response("All menu items for current user are deleted")
    
    def post(self, request, *arg, **kwargs):
        serialized_item = CartSerializer(data=request.data)
        serialized_item.is_valid(raise_exception=True)
        id = request.data['menuitem']
        quantity = request.data['quantity']
        item = get_object_or_404(MenuItem, id=id)
        price = int(quantity) * item.price
        Cart.objects.create(user=request.user, quantity=quantity, unit_price=item.price, price=price, menuitem_id=id)
        return Response('Item added to the cart')
        
        


# admin = dbcd5c252275d41c4baa5759523c7fed081c983d
# janedoe = b5181c578adb5d3b89e49764cfa1885f45ae252b
