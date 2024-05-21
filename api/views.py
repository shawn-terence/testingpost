from api.models import User, Customer, Farmer, Animal,Orders
from api.serializers import (
    UserSerializer,
    FarmerSerializer,
    CustomerSerializer,
    AnimalSerializer,
    OrderSerializer,
)
from django.contrib.auth import authenticate, login
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics

class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        if user:
            return Response({'username': user.username})
        else:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
class UserRegistrationView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AnimalViewing(generics.ListCreateAPIView):
    queryset = Animal.objects.all()
    serializer_class = AnimalSerializer

class AnimalViewingFarmer(generics.ListCreateAPIView):
    serializer_class = AnimalSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == "farmer":
            return Animal.objects.filter(farmer=user.farmer_account)
        return Animal.objects.none()
class CustomerRegistrationView(APIView):
    def post(self, request):
        serializer = CustomerSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FarmerRegistrationView(APIView):
    def post(self, request):
        serializer = FarmerSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class StudentRegistrationView(APIView):
    def post(self, request):
        serializer = StudentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class UserLoginView(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        username = request.data.get("username")
        password = request.data.get("password")

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            token, created = Token.objects.get_or_create(user=user)
            if created:
                token.delete() 
                token = Token.objects.create(user=user)

            response_data = {
                "token": token.key,
                "username": user.username,
                "role": user.role,
            }

            if user.role == "customer":
                customer = (
                    user.customer_account
                )  # Assuming the related name is "student_account"
                if customer is not None:
                    # Add customer data to the response data
                    customer_data = CustomerSerializer(customer).data
                    response_data["data"] = customer_data

            elif user.role == "farmer":
                farmer = (
                    user.farmer_account
                )  # Assuming the related name is "student_account"
                if farmer is not None:
                    # Add farmer data to the response data
                    farmer_data = FarmerSerializer(farmer).data
                    response_data["data"] = farmer_data
            return Response(response_data)
        else:
            return Response(
                {"message": "Invalid username or password"},
                status=status.HTTP_401_UNAUTHORIZED,
            )


class AnimalCreationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = AnimalSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        print(request.headers)
        token_key = request.auth.key
        token = Token.objects.get(key=token_key)
        token.delete()

        return Response({"detail": "Successfully logged out."})


class CreateOrderView(APIView):
    def post(self, request):
        serializer = OrderSerializer(data=request.data)
        if serializer.is_valid():
            # Infer farmer from the provided animal
            animal = serializer.validated_data["animal"]
            serializer.validated_data["farmer"] = animal.farmer

            # Decrease the available quantity of the animal
            quantity = serializer.validated_data["quantity"]
            animal.available -= quantity
            animal.save()

            # Save the order
            serializer.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#######
class OrderListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer

    def get_queryset(self):
        user = self.request.user
        print(user.username)
        if user.role == "customer":
            customer_id = self.request.data.get('customer_id')
            return Orders.objects.filter(customer_id=customer_id)
        elif user.role == "farmer":
            return Orders.objects.filter(
                 #farmer=user.farmer_account,order_status=("accepted"))
                 farmer=user.farmer_account
            )
        else:
            print("nothing")
            return Orders.objects.none()
class OrderAcceptView(APIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    def put(self, request, pk):
        user = request.user
        if user.role != "farmer":
            return Response(
                {"message": "Only farmers can update order status"},
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            order = Orders.objects.get(pk=pk)
        except Orders.DoesNotExist:
            return Response(
                {"message": "Order not found"}, status=status.HTTP_404_NOT_FOUND
            )

        action = request.data.get("action")
        if action == "accept":
            order.order_status = "accepted"
            order.save()
        elif action == "deny":
            animal = order.animal
            quantity = order.quantity
            animal.available += quantity
            animal.save()

            order.order_status = "denied"
            order.save()
        else:
            return Response(
                {"message": "Invalid action"}, status=status.HTTP_400_BAD_REQUEST
            )

        return Response({"message": f"Order {action.capitalize()}ed successfully"})