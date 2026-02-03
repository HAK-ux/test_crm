from django.contrib import admin
from django.urls import path
from .views import (restaurant_list, customer_list, order_list, 
                   restaurant_detail, customer_detail, order_detail,
                   restaurant_dashboard, restaurant_dashboard_refresh)

urlpatterns = [
    path("restaurants/", restaurant_list),
    path("restaurants/<int:pk>/", restaurant_detail),
    path("restaurants/<int:pk>/dashboard/", restaurant_dashboard),

    path("customers/", customer_list),
    path("customers/<int:pk>/", customer_detail),

    path("orders/", order_list),
    path("orders/<int:pk>/", order_detail),
    
    path("restaurants/<int:pk>/dashboard/refresh/", restaurant_dashboard_refresh),
]
