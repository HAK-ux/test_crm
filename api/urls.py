from django.contrib import admin
from django.urls import path
from .views import restaurant_list, customer_list, order_list

urlpatterns = [
    path("restaurants/", restaurant_list),
    path("customers/", customer_list),
    path("orders/", order_list),
]
