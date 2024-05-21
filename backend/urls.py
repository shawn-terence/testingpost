from django.contrib import admin
from django.urls import path
from api.views import (
    UserRegistrationView,
    UserLoginView,
    UserLogoutView,
    FarmerRegistrationView,
    CustomerRegistrationView,
    AnimalCreationView,
    AnimalViewing,
    CreateOrderView,
    OrderListView,
    OrderAcceptView,
    UserProfileView,
    AnimalViewingFarmer
)
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/user/profile",UserProfileView.as_view(),name="profile"),
    path("api/animals/", AnimalViewing.as_view(), name="animals"),
    path("api/orders/create/", CreateOrderView.as_view(), name="order-create"),
    path("api/orders/", OrderListView.as_view(), name="order-list"),
    path("api/orders/accept/<int:pk>/", OrderAcceptView.as_view(), name="order-accept"),
    path("api/animals/farmer/", AnimalViewingFarmer.as_view(), name="animals-farmer"),

    #path(
       # "api/auth/register/", UserRegistrationView.as_view(), name="user-registration"
   # ),
    path("api/animals/add/", AnimalCreationView.as_view(), name="animal-creation"),
    path("api/auth/login/", UserLoginView.as_view(), name="user-login"),
    path("api/auth/logout/", UserLogoutView.as_view(), name="user-logout"),
    path(
        "api/farmer/register/",
        FarmerRegistrationView.as_view(),
        name="farmer-registration",
    ),
    path(
        "api/customer/register/",
        CustomerRegistrationView.as_view(),
        name="customer-registration",
    ),
    # Add other URLs here
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
