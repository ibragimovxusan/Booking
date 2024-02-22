from django.urls import path
from . import views

urlpatterns = [
    path("Register/", views.RegisterUserAPIView.as_view(), name="Register"),
    path("Profiles/", views.BarberUserListCreateAPIView.as_view(), name="GetOrCreateBarber"),
    path("Profile/", views.UserOrBarberRetrieveUpdateAPIView.as_view(), name="GetOrUpdateBarber"),
    path("Companies/", views.CompanyListAPIView.as_view(), name="GetCompany"),
    path("Company/", views.CompanyCreateAPIView.as_view(), name="CreateCompany"),
    path("Company/<int:pk>/", views.CompanyRetrieveUpdateAPIView.as_view(), name="GetOrUpdateCompany"),
]
