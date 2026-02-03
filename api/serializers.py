from rest_framework import serializers
from .models import Restaurant, Order, Customer


class RestaurantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Restaurant
        fields = ["id", "name", "created_at"]

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ["id", "restaurant", "email", "created_at"]

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ["id", "restaurant", "customer", "total_amount", "created_at"]