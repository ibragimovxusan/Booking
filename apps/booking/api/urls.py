from django.urls import path
from . import views

urlpatterns = [
    path('Booking/', views.BookingCreateAPIView.as_view(), name='CreateBooking'),
    path('Bookings/', views.BookingListAPIView.as_view(), name='ListBooking'),
    path('Booking/<int:pk>/', views.BookingDetailAPIView.as_view(), name='DetailBooking'),
    path('Room/<int:pk>/Availability/', views.RoomAvailabilityRetrieveView.as_view(), name='RoomAvailability'),
    path('Room/', views.RoomBookingAPIView.as_view(), name='ListRoom'),
]
