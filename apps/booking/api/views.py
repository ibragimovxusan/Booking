from datetime import datetime
from django.db.models import Q
from django.utils import timezone
from apps.account.models import User
from apps.booking.models import Booking
from rest_framework import generics, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated

from .serializers import (
    BookingListSerializer,
    BookingDetailSerializer,
    BookingCreatedSerializer,
    RoomAvailabilitySerializer
)


class BookingCreateAPIView(generics.CreateAPIView):
    serializer_class = BookingCreatedSerializer
    queryset = Booking.objects.all()
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(resident=self.request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class BookingListAPIView(generics.ListAPIView):
    serializer_class = BookingListSerializer
    queryset = Booking.objects.all()
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(resident=self.request.user).order_by('-id')


class BookingDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = BookingDetailSerializer
    queryset = Booking.objects.all()
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(resident=self.request.user).order_by('-id')

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return BookingDetailSerializer
        return BookingCreatedSerializer

    def perform_update(self, serializer):
        if serializer.instance.resident != self.request.user:
            return Response({'error': 'You are not allowed to perform this action'}, status=status.HTTP_403_FORBIDDEN)
        serializer.save(resident=self.request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        curr_time = timezone.now().time()
        instance = self.get_object()
        if instance.resident != self.request.user:
            return Response({'error': 'You are not allowed to perform this action'}, status=status.HTTP_403_FORBIDDEN)
        if curr_time.hour + 1 >= instance.start:
            return Response({'error': "You can't delete because the booking is less than an hour away"},
                            status=status.HTTP_403_FORBIDDEN)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class RoomAvailabilityRetrieveView(generics.ListAPIView):
    serializer_class = RoomAvailabilitySerializer

    def get_queryset(self):
        room_id = self.kwargs.get('pk')
        curr_time = self.request.GET.get('date', timezone.now().strftime("%d-%m-%Y"))

        # Parse date string to datetime object
        obj_date = datetime.strptime(curr_time, '%d-%m-%Y')
        cur_date = datetime(obj_date.year, obj_date.month, obj_date.day)

        # Retrieve bookings for the given room and date
        bookings = Booking.objects.filter(
            Q(room_id=room_id),
            Q(Q(start__date=cur_date) | Q(end__date=cur_date))
        ).order_by('start')

        # Retrieve room details
        room = User.objects.get(id=room_id)
        room_open = room.start
        room_close = room.end

        booked_slots, room_open = self.booking_slots(cur_date, room_open, room_close, bookings)

        return self.date_availability(curr_time, room_open, room_close, booked_slots)

    @staticmethod
    def booking_slots(cur_date, room_open, room_close, bookings):
        slots = []
        for booking in bookings:
            if booking.start.date() == cur_date.date():
                start_time = booking.start.time()
            else:
                start_time = room_open

            if booking.end.date() == cur_date.date():
                end_time = booking.end.time()
            else:
                end_time = room_close

            slots.append((start_time, end_time))
        return slots, room_open

    @staticmethod
    def date_availability(curr_time, room_open, room_close, booked_slots):
        # Calculate available time slots
        availability_list = []
        previous_end = room_open

        for start, end in booked_slots:
            if previous_end < start:
                availability_list.append({
                    "start": f"{curr_time} {previous_end}",
                    "end": f"{curr_time} {start}"
                })
            previous_end = end

        if previous_end < room_close:
            availability_list.append({
                "start": f"{curr_time} {previous_end}",
                "end": f"{curr_time} {room_close}"
            })

        return availability_list


class RoomBookingAPIView(generics.CreateAPIView):
    queryset = Booking.objects.all()
    serializer_class = BookingCreatedSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)


def parse_time(time):
    obj_date = timezone.strptime(time, '%d-%m-%Y %H:%M:%S')
    cur = obj_date.strftime("%Y-%m-%d %H:%M:%S")
    return cur
