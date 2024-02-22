from datetime import datetime
from django.db.models import Q
from apps.account.models import User
from apps.booking.models import Booking
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .serializers import (
    BookingListSerializer,
    RoomBookingSerializer,
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
        curr_time = datetime.now().time()
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
        room_id = self.kwargs['pk']
        curr_time = self.request.GET.get('date', datetime.now().strftime("%d-%m-%Y"))
        obj_date = datetime.strptime(curr_time, '%d-%m-%Y')
        cur = obj_date.strftime("%Y-%m-%d")
        cur_date = datetime.strptime(cur, "%Y-%m-%d")

        queryset = Booking.objects.filter(
            Q(room_id=room_id),
            Q(Q(start__day=cur_date.day) | Q(end__day=cur_date.day))
        ).order_by('start')

        room = User.objects.get(id=room_id)
        start = room.start
        end = room.end

        booked_list = []

        for booked in queryset:
            if booked.start.date() == cur_date.date():
                start = booked.start.time()

            if booked.end.date() == cur_date.date():
                end = booked.end.time()

            booked_list.append((start, end))

        availability_list = []
        previous_end = room.open

        for start, end in booked_list:

            if previous_end < start:
                availability_list.append({
                    "start": f"{curr_time} {previous_end}",
                    "end": f"{curr_time} {start}"
                })

            previous_end = end

        if previous_end < room.end:
            availability_list.append({
                "start": f"{curr_time} {previous_end}",
                "end": f"{curr_time} {room.end}"
            })

        return availability_list


class RoomBookingAPIView(generics.CreateAPIView):
    queryset = Booking.objects.all()
    serializer_class = BookingCreatedSerializer

    def create(self, request, *args, **kwargs):
        room_id = request.data.get('room')
        resident = request.user
        a = request.data.get('start')
        b = request.data.get('end')
        start = parse_time(a)
        end = parse_time(b)

        if start > end:
            return Response({'error': 'Start time cannot be greater than end time'}, status=status.HTTP_400_BAD_REQUEST)

        if start < datetime.now().time():
            return Response({'error': 'You cannot book a room in the past'}, status=status.HTTP_400_BAD_REQUEST)

        room = User.objects.get(id=room_id)
        if room.start > start or room.end < end:
            return Response({'error': 'Room is not available at this time'}, status=status.HTTP_400_BAD_REQUEST)

        queryset = Booking.objects.filter(
            Q(room_id=room_id),
            Q(Q(start__day=start.day) | Q(end__day=end.day))
        ).order_by('start')

        for booking in queryset:
            if booking.start <= start <= booking.end or booking.start <= end <= booking.end:
                return Response({'error': 'Room is already booked at this time'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(resident=resident)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


def parse_time(time):
    obj_date = datetime.strptime(time, '%d-%m-%Y %H:%M:%S')
    cur = obj_date.strftime("%Y-%m-%d %H:%M:%S")
    return cur