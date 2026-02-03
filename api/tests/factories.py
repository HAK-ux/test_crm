import factory
from decimal import Decimal
from django.utils import timezone
from api.models import Restaurant, Customer, Order


class RestaurantFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Restaurant

    name = factory.Sequence(lambda n: f"Restaurant {n}")


class CustomerFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Customer

    restaurant = factory.SubFactory(RestaurantFactory)
    email = factory.Sequence(lambda n: f"user{n}@example.com")


class OrderFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Order

    restaurant = factory.SubFactory(RestaurantFactory)
    customer = factory.SubFactory(CustomerFactory)
    total_amount = Decimal("10.00")
    created_at = factory.LazyFunction(timezone.now)