from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Restaurant, Customer, Order
from .serializers import RestaurantSerializer, CustomerSerializer, OrderSerializer
from django.utils import timezone
from django.db.models.functions import Coalesce
from datetime import timedelta
from django.db.models import Sum, Count, Avg, DecimalField
from django.core.cache import cache

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
        serializer = CustomerSerializer(data=request.data)
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
            for d in [7, 30, 90]:
                cache.delete(f"dashboard:restaurant:{serializer.data['restaurant']}:days:{d}")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(["GET", "PUT", "POST"])
def restaurant_detail(request, pk: int):
    try:
        restaurant = Restaurant.objects.get(pk=pk)
    except Restaurant.DoesNotExist:
        return Response("Not found.", status=status.HTTP_404_NOT_FOUND)
    
    if request.method == "GET":
        serializer = RestaurantSerializer(restaurant)
        return Response(serializer.data)
    
    elif request.method == "PUT":
        serializer = RestaurantSerializer(restaurant, data=request.data)
        if serializer.is_valid():
            serializer.save() # updates existing restaurant
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == "DELETE":
        restaurant.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(["GET", "PUT", "DELETE"])
def customer_detail(request, pk: int):
    try:
        customer = Customer.objects.get(pk=pk)
    except Customer.DoesNotExist:
        return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

    if request.method == "GET":
        serializer = CustomerSerializer(customer)
        return Response(serializer.data)

    elif request.method == "PUT":
        serializer = CustomerSerializer(customer, data=request.data)
        if serializer.is_valid():
            serializer.save()  # updates existing customer
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == "DELETE":
        customer.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(["GET", "PUT", "DELETE"])
def order_detail(request, pk: int):
    try:
        order = Order.objects.select_related("restaurant", "customer").get(pk=pk)
    except Order.DoesNotExist:
        return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

    if request.method == "GET":
        serializer = OrderSerializer(order)
        return Response(serializer.data)

    elif request.method == "PUT":
        serializer = OrderSerializer(order, data=request.data)
        if serializer.is_valid():
            serializer.save()  # updates existing order
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == "DELETE":
        order.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(["GET"])
def restaurant_dashboard(request, pk: int):
    #validate restaurant exists
    try:
        restaurant = Restaurant.objects.get(pk=pk)
    except Restaurant.DoesNotExist:
        return Response("NOT FOUND", status=status.HTTP_404_NOT_FOUND)

    try:
        days = int(request.query_params.get("days", 7))
        if days <= 0 or days > 365:
            raise ValueError()
    except ValueError:
        return Response({"detail": "days must be an integer between 1 and 365."},
                        status=status.HTTP_400_BAD_REQUEST)

    since = timezone.now() - timedelta(days=days)
    
    cache_key = f"dashboard:restaurant:{pk}:days:{days}"

    cached = cache.get(cache_key)
    if cached is not None:
        return Response(cached)
    
    orders_qs = Order.objects.filter(restaurant=restaurant, created_at__gte=since)

    # Aggregate totals
    totals = orders_qs.aggregate(
    orders_count=Count("id"),
    revenue_total=Coalesce(
        Sum("total_amount"),
        0,
        output_field=DecimalField(max_digits=10, decimal_places=2),
    ),
    avg_order_value=Coalesce(
        Avg("total_amount"),
        0,
        output_field=DecimalField(max_digits=10, decimal_places=2),
    ),
    unique_customers=Count("customer_id", distinct=True),
)

    # Top customers by spend (limit 5)
    top_customers = (
    orders_qs.values("customer_id", "customer__email")
    .annotate(
        total_spend=Coalesce(
            Sum("total_amount"),
            0,
            output_field=DecimalField(max_digits=10, decimal_places=2),
            ),
        orders=Count("id"),
        )
    .order_by("-total_spend")[:5]
    )   

    data = {
        "restaurant": {"id": restaurant.id, "name": restaurant.name},
        "window_days": days,
        "since": since.isoformat(),
        "totals": {
            "orders_count": totals["orders_count"],
            "revenue_total": str(totals["revenue_total"]),      # Decimal -> string for JSON
            "avg_order_value": str(totals["avg_order_value"]),  # Decimal -> string for JSON
            "unique_customers": totals["unique_customers"],
        },
        "top_customers": [
            {
                "customer_id": row["customer_id"],
                "email": row["customer__email"],
                "total_spend": str(row["total_spend"]),
                "orders": row["orders"],
            }
            for row in top_customers
        ],
    }

    cache.set(cache_key, data, timeout=60)  # cache for 60s
    return Response(data)