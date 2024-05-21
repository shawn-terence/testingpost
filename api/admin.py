from django.contrib import admin
from .models import Farmer, Customer, User, Animal

# Register your models here.
admin.site.register(Farmer)
admin.site.register(Customer)
admin.site.register(User)
admin.site.register(Animal)
