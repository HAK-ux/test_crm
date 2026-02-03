from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .models import Restaurant, Customer, Order
from .serializers import RestaurantSerializer, CustomerSerializer, OrderSerializer

@api_view(["GET", "POST"])
def restaurant_list(request):
    if request.method == "GET":
        restaurants = Restaurant.objects.all()
        serializer = RestaurantSerializer(restaurants, many=True)
        return Response(serializer.data)
    
    elif request.method == "POST":
        serializer = RestaurantSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(["GET", "POST"])
def customer_list(request):
    if request.method == "GET":
        customers = Customer.objects.all()
        serializer = CustomerSerializer(customers, many=True)
        return Response(serializer.data)
    
    elif request.method == "POST":
        serializer = CustomerSerializer(request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(["GET", "POST"])
def order_list(request):
    if request.method == "GET":
        orders = Order.objects.select_related("restaurant", "customer") # When you fetch Orders, also fetch their related Restaurant and Customer in the same query
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)
    
    elif request.method == "POST":
        serializer = OrderSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)