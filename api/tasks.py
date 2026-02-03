from celery import shared_task
from django.db.models import Sum, Count
from django.db.models.functions import Coalesce
from django.core.cache import cache

from .models import Order, Restaurant


@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=True, max_retries=5)
def recompute_dashboard_cache(self, restaurant_id: int, days: int = 7) -> dict:
    """
    Example background task:
    - recompute dashboard totals
    - store them in Redis cache
    """
    restaurant = Restaurant.objects.get(id=restaurant_id)

    orders_qs = Order.objects.filter(restaurant=restaurant)

    totals = orders_qs.aggregate(
        orders_count=Count("id"),
        revenue_total=Coalesce(Sum("total_amount"), 0),
    )

    data = {
        "restaurant": {"id": restaurant.id, "name": restaurant.name},
        "window_days": days,
        "totals": {
            "orders_count": totals["orders_count"],
            "revenue_total": str(totals["revenue_total"]),
        },
        "generated_by": "celery",
    }

    cache_key = f"dashboard:restaurant:{restaurant_id}:days:{days}"
    cache.set(cache_key, data, timeout=60)
    return data