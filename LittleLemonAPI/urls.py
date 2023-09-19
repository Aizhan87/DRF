from django.urls import path
from . import views

urlpatterns = [
    path('menu-items', views.MenuItems.as_view()),
    path('menu-items/category', views.CategoryView.as_view()),
    path('menu-items/<int:pk>', views.MenuItemView.as_view()),
    path('groups/manager/users', views.ManagerListView.as_view()),
    path('groups/manager/users/<int:pk>', views.ManagerDeleteView.as_view()),
    path('groups/delivery-crew/users', views.DeliveryCrewListView.as_view()),
]
