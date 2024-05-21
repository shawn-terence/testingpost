from rest_framework import serializers
from .models import User, Customer, Farmer, Animal, Orders
from django.utils import timezone


class OrderSerializer(serializers.ModelSerializer):
    animal_name = serializers.CharField(source='animal.animal_name', read_only=True)
    class Meta:
        model = Orders
        fields = [
            "order_id",
            "customer",
            "animal",
            "quantity",
            "order_status",
            "animal_name"
        ]  # Exclude order_date, order_status, and farmer
       # fields = '__all__'
        
        
    def create(self, validated_data):
        animal = validated_data["animal"]
        print(animal)
        # Automatically set order_date to the current time
        validated_data["order_date"] = timezone.now()
        # Default order_status to 'pending'
        validated_data["animal_name"] = animal.animal_name
        validated_data["order_status"] = "pending"
        return super().create(validated_data)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username", "email", "role", "password"]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class CustomerSerializer(serializers.ModelSerializer):
    user = UserSerializer()  # Remove read_only=True to allow creation of User

    class Meta:
        model = Customer
        fields = "__all__"

    def create(self, validated_data):
        user_data = validated_data.pop("user")  # Access 'user' data correctly
        user_serializer = UserSerializer(data=user_data)
        if user_serializer.is_valid():
            user = user_serializer.save()  # Save user instance
            customer = Customer.objects.create(
                user=user, **validated_data
            )  # Create Customer instance
            return customer
        else:
            raise serializers.ValidationError(user_serializer.errors)


class FarmerSerializer(serializers.ModelSerializer):
    user = UserSerializer()  # Remove read_only=True to allow creation of User

    class Meta:
        model = Farmer
        fields = "__all__"

    def create(self, validated_data):
        user_data = validated_data.pop("user")  # Access 'user' data correctly
        user_serializer = UserSerializer(data=user_data)
        if user_serializer.is_valid():
            user = user_serializer.save()  # Save user instance
            farmer = Farmer.objects.create(
                user=user, **validated_data
            )  # Create Farmer instance
            return farmer
        else:
            raise serializers.ValidationError(user_serializer.errors)


class AnimalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Animal
        fields = "__all__"

    def create(self, validated_data):
        # Get the user making the request
        user = self.context["request"].user

        # Check if the user has the role of 'farmer'
        if user.role == "farmer":
            # Ensure the validated_data contains 'farmer' field
            if "farmer" not in validated_data:
                raise serializers.ValidationError("A farmer must be specified.")

            # Associate the farmer with the animal
            farmer = validated_data.pop("farmer")
            animal = Animal.objects.create(farmer=farmer, **validated_data)
            return animal
        else:
            # Raise validation error if user is not a farmer
            raise serializers.ValidationError("Only farmers can create animals.")
