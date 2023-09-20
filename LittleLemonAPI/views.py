from django.http import JsonResponse, HttpResponseBadRequest
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.models import User, Group
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status, generics
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .models import MenuItem, Category, Cart, Order, OrderItem
from .serializers import MenuItemSerializer, CategorySerializer, ManagerListSerializer, CartSerializer, OrderSerializer, SingleOrderSerializer
import math
from datetime import date
from .permissions import IsManager, IsDeliveryCrew


class MenuItems(generics.ListCreateAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer

    def get_permissions(self):
        if self.request.method != 'GET':
            self.permission_classes = [IsAuthenticated, IsManager or IsAdminUser]
        return super(MenuItems, self).get_permissions()


class CategoryView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsManager or IsAdminUser]


class MenuItemView(generics.RetrieveUpdateDestroyAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer

    def get_permissions(self):
        permission_classes = [IsAuthenticated]
        if self.request.method == 'PATCH' or 'DELETE':
            permission_classes = [IsAuthenticated,  IsManager or IsAdminUser]
        return [permission() for permission in permission_classes]


class ManagerListView(generics.ListCreateAPIView):
    queryset = User.objects.filter(groups__name='Manager')
    serializer_class = ManagerListSerializer
    permission_classes = [IsAuthenticated, IsManager or IsAdminUser]

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
    permission_classes = [IsAuthenticated, IsManager or IsAdminUser]

    def delete(self, request, *args, **kwargs):
        pk = self.kwargs['pk']
        user = get_object_or_404(User, pk=pk)
        managers = Group.objects.get(name='Manager')
        managers.user_set.remove(user)
        return JsonResponse(status=200, data={'message': 'User is removed from Manager group'})


class DeliveryCrewListView(generics.ListCreateAPIView):
    queryset = User.objects.filter(groups__name='Delivery Crew')
    serializer_class = ManagerListSerializer
    permission_classes = [IsAuthenticated, IsManager or IsAdminUser]

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
    permission_classes = [IsAuthenticated, IsManager or IsAdminUser]

    def delete(self, request, *args, **kwargs):
        pk = self.kwargs['pk']
        user = get_object_or_404(User, pk=pk)
        delivery_crew = Group.objects.get(name='Delivery Crew')
        delivery_crew.user_set.remove(user)
        return JsonResponse(status=200, data={'message': 'User is removed from Delivery Crew group'})
    

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

class OrderListView(generics.ListCreateAPIView):
    serializer_class = OrderSerializer
    
    def get_queryset(self, *args, **kwargs):
        if self.request.user.groups.filter(name='Manager').exists() or self.request.user.is_superuser == True:
            queryset = Order.objects.all()
        elif self.request.user.groups.filter(name='Delivery Crew').exists():
            queryset = Order.objects.filter(delivery_crew=self.request.user)
        else:
            queryset = Order.objects.filter(user=self.request.user)
        return queryset
    
    def get_permissions(self):
        if self.request.method == 'GET' or 'POST':
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsAuthenticated, IsManager or IsAdminUser]
        return [permission() for permission in permission_classes]
    
    def post(self, request, *args, **kwargs):
        cart = Cart.objects.filter(user=request.user)
        values=cart.values_list()
        if len(values) == 0:
            return HttpResponseBadRequest()
        total = math.fsum([float(value[-1]) for value in values])
        try:
            order = Order.objects.create(user=request.user, status=False, total=total, date=date.today())
            for i in cart.values():
                menuitem = get_object_or_404(MenuItem, id=i['menuitem_id'])
                orderitem = OrderItem.objects.create(order=self.request.user, menuitem=menuitem, quantity=i['quantity'])
                orderitem.save()
            cart.delete()
        except:
            return Response('Your order has been placed! Your order number is {}'.format(str(order.id)))
        return Response('Your order has been placed! Your order number is {}'.format(str(order.id)))
            

class SingleOrderView(generics.ListCreateAPIView):
    serializer_class = SingleOrderSerializer
    
    def get_permissions(self):
        order = Order.objects.get(pk=self.kwargs['pk'])
        if self.request.user == order.user and self.request.method == 'GET':
            permission_classes = [IsAuthenticated]
        elif self.request.method == 'PUT' or self.request.method == 'DELETE':
            permission_classes = [IsAuthenticated, IsManager | IsAdminUser]
        else:
            permission_classes = [IsAuthenticated, IsDeliveryCrew | IsManager | IsAdminUser]
        return[permission() for permission in permission_classes] 

    def get_queryset(self, *args, **kwargs):
            query = OrderItem.objects.filter(order_id=self.kwargs['pk'])
            return query
        
    def delete(self, request, *args, **kwargs):
        order = Order.objects.get(pk=self.kwargs['pk'])
        order_number = str(order.id)
        order.delete()
        return JsonResponse(status=200, data={'message':'Order #{} was deleted'.format(order_number)})
        


# admin = dbcd5c252275d41c4baa5759523c7fed081c983d
# janedoe = b5181c578adb5d3b89e49764cfa1885f45ae252b --> delivery crew
# jimmydoe = caaba0f4d44d071312e0cf276de32fa455c94ca5 --> customer
# admin_1 = 3bb70e788ebb18ce1de6638f9e85bfa7a2fa4645  --> manager
# johndoe = d93c4c2f2ecfa3a75c5f89aad2f9253a47babf1f  --> manager