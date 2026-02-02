from django.db import models

# Create your models here.

class Restaurant(models.Model):
    name = models.CharField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Customer(models.Model):
    restaurant = models.ForeignKey(
        Restaurant, 
        on_delete=models.CASCADE, # if parent object is deleted, automatically delete all related child objects
        related_name="customers",
    )
    email = models.EmailField()
    created_at = models.DateTimeField(auto_now_add=True)

    
    class Meta:
        indexes = [
            models.Index(fields=["restaurant", "created_at"]),
        ]

    def __str__(self):
        return self.email

class Order(models.Model):
    restaurant = models.ForeignKey(
        Restaurant, 
        on_delete=models.CASCADE, # if parent object is deleted, automatically delete all related child objects
        related_name="orders",
    )
    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name="orders",
    )

    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["restaurant", "created_at"]),
            models.Index(fields=["customer", "created_at"])
        ]
    
    def __str__(self):
        return f"Order {self.id}"