from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Restaurant, Customer, Order

admin.site.register(Restaurant)
admin.site.register(Customer)
admin.site.register(Order)