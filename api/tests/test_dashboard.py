import pytest
from decimal import Decimal
from django.core.cache import cache
from django.utils import timezone
from datetime import timedelta

from api.models import Order
from api.tests.factories import (
    RestaurantFactory,
    CustomerFactory,
    OrderFactory,
)

@pytest.mark.django_db
def test_dashboard_aggregates_correctly(api_client):
    cache.clear()

    r = RestaurantFactory()
    c1 = CustomerFactory(restaurant=r, email="a@example.com")
    c2 = CustomerFactory(restaurant=r, email="b@example.com")

    # 3 orders in the window (days=7)
    OrderFactory(restaurant=r, customer=c1, total_amount=Decimal("10.00"))
    OrderFactory(restaurant=r, customer=c1, total_amount=Decimal("20.00"))
    OrderFactory(restaurant=r, customer=c2, total_amount=Decimal("30.00"))

    # one old order outside window
    old_time = timezone.now() - timedelta(days=20)
    old_order = Order.objects.create(
    restaurant=r,
    customer=c2,
    total_amount=Decimal("999.00"),
    )

    # force the timestamp to be old (bypass auto_now_add)
    Order.objects.filter(id=old_order.id).update(created_at=old_time)
    
    resp = api_client.get(f"/api/restaurants/{r.id}/dashboard/?days=7")
    assert resp.status_code == 200

    data = resp.json()
    assert data["restaurant"]["id"] == r.id
    assert data["window_days"] == 7

    totals = data["totals"]
    assert totals["orders_count"] == 3
    assert totals["unique_customers"] == 2
    assert totals["revenue_total"] == "60.00"
    assert totals["avg_order_value"] == "20.00"

    # top customer should be c2 with 30 spend or c1 with 30 spend (tie possible)
    top = data["top_customers"]
    assert len(top) >= 1
    assert "email" in top[0]
    assert "total_spend" in top[0]

@pytest.mark.django_db
def test_dashboard_uses_cache(api_client):
    cache.clear()

    r = RestaurantFactory()
    c = CustomerFactory(restaurant=r)
    OrderFactory(restaurant=r, customer=c, total_amount=Decimal("10.00"))

    # First request: compute and cache
    resp1 = api_client.get(f"/api/restaurants/{r.id}/dashboard/?days=7")
    assert resp1.status_code == 200
    data1 = resp1.json()

    # Modify DB after caching
    OrderFactory(restaurant=r, customer=c, total_amount=Decimal("999.00"))

    # Second request: should return cached result (still old total) within TTL
    resp2 = api_client.get(f"/api/restaurants/{r.id}/dashboard/?days=7")
    assert resp2.status_code == 200
    data2 = resp2.json()

    assert data2["totals"]["revenue_total"] == data1["totals"]["revenue_total"]