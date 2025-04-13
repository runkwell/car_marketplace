from django.db import models
from django.contrib.auth.models import User

class Brand(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Car(models.Model):
    CONDITION_CHOICES = [
        ('new', 'New'),
        ('used', 'Used'),
    ]
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('sold', 'Sold'),  # Thêm trạng thái sold
    ]
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)
    model = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    year = models.IntegerField()
    condition = models.CharField(max_length=10, choices=CONDITION_CHOICES)
    location = models.CharField(max_length=100)
    description = models.TextField()
    mileage = models.IntegerField(null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    def __str__(self):
        return f"{self.brand} {self.model} ({self.year})"

class CarImage(models.Model):
    car = models.ForeignKey(Car, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='images/')

    def __str__(self):
        return f"Image for {self.car}"

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    car = models.ForeignKey(Car, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"Notification for {self.user.username}: {self.message}"

class PurchaseRequest(models.Model):
    car = models.ForeignKey(Car, on_delete=models.CASCADE)
    buyer_name = models.CharField(max_length=100)
    buyer_email = models.EmailField()
    buyer_phone = models.CharField(max_length=15)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Purchase request for {self.car} by {self.buyer_name}"
