from django.db import models
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from rest_framework.authtoken.models import Token


class User(AbstractUser):
    ROLE_CHOICES = (
        ("farmer", "Farmer"),
        ("customer", "Customer"),
    )

    role = models.CharField(max_length=15, choices=ROLE_CHOICES)


class Customer(models.Model):
    profile_picture = models.ImageField(default="fall.png", blank=True)
    customer_id = models.AutoField(primary_key=True)
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="customer_account"
    )


class Farmer(models.Model):
    profile_picture = models.ImageField(default="fall.png", blank=True)
    farmer_id = models.AutoField(primary_key=True)
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="farmer_account"
    )
    contact = models.CharField(max_length=25)


class Animal(models.Model):
    animal_picture = models.ImageField(default="fall.png", blank=True)
    animal_id = models.AutoField(primary_key=True)
    animal_name = models.CharField(max_length=50)
    animal_type = models.CharField(max_length=50)
    animal_age = models.CharField(max_length=10)
    animal_location = models.CharField(max_length=30)
    animal_breed = models.CharField(max_length=20)
    available = models.IntegerField()
    farmer = models.ForeignKey(Farmer, on_delete=models.CASCADE, related_name="animals")
    animal_price = models.IntegerField()
    animal_description = models.CharField(max_length=200)


class Orders(models.Model):
    ORDER_STATUS = (
        ("pending", "Pending"),
        ("accepted", "Accepted"),
        ("denied", "Denied"),
    )
    order_id = models.AutoField(primary_key=True)
    customer = models.ForeignKey(
        Customer, on_delete=models.CASCADE, related_name="orders"
    )
    animal = models.ForeignKey(Animal, on_delete=models.CASCADE, related_name="orders")
    farmer = models.ForeignKey(Farmer, on_delete=models.CASCADE, related_name="orders")
    order_date = models.DateField(auto_now_add=True)
    animal_name=models.CharField(max_length=30)
    quantity = models.IntegerField(blank=True)
    order_status = models.CharField(max_length=20, choices=ORDER_STATUS, blank=True)
