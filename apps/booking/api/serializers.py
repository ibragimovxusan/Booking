from datetime import datetime

from rest_framework import serializers

from apps.account.api.serializers import UserSerializer, BarberUserSerializer
from apps.booking.models import Booking


class BookingCreatedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = ('id', 'room', 'resident', 'start', 'end', 'created_at')
        extra_kwargs = {
            'resident': {'read_only': True},
            'created_at': {'read_only': True},
        }

    def create(self, validated_data):
        resident = self.context['request'].user
        start = validated_data.get('start')
        end = validated_data.get('end')
        room = validated_data.get('room')

        if Booking.objects.filter(room=room, start__lte=start, end__gte=start).exists() or \
                Booking.objects.filter(room=room, start__lte=end, end__gte=end).exists() or \
                Booking.objects.filter(room=room, start__gte=start, end__lte=end).exists():
            raise serializers.ValidationError("The room is already booked for that time")

        if start > end:
            raise serializers.ValidationError("Start time cannot be greater than end time")

        booking = Booking.objects.create(**validated_data)
        return booking


class BookingListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = ('id', 'room', 'resident', 'start', 'end', 'created_at')


class BookingDetailSerializer(serializers.ModelSerializer):
    room = BarberUserSerializer(read_only=True)
    resident = UserSerializer(read_only=True)

    class Meta:
        model = Booking
        fields = ('id', 'room', 'resident', 'start', 'end', 'created_at')
        extra_kwargs = {
            'resident': {'read_only': True},
            'room': {'read_only': True}
        }

    def update(self, instance, validated_data):
        curr_time = datetime.now().time()
        if curr_time > instance.start:
            raise serializers.ValidationError("You can't update a booking that has already started")
        if curr_time.hour + 1 >= instance.start.hour:
            raise serializers.ValidationError("You can't update because the booking is less than an hour away")
        instance.start = validated_data.get('start', instance.start)
        instance.end = validated_data.get('end', instance.end)
        instance.save()
        return instance


class RoomAvailabilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = ('start', 'end')


#
# class RoomSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Room
#         fields = ('id', 'name', 'type', 'capacity')
#
#
#
# class UserSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = User
#         fields = ('name',)
#
#
# class RoomNotAvailabilitySerializer(serializers.ModelSerializer):
#     resident = UserSerializer(read_only=True)
#
#     class Meta:
#         model = Book
#         fields = ('resident', 'start', 'end')
#
#
class RoomBookingSerializer(serializers.ModelSerializer):
    resident = UserSerializer(write_only=True)

    class Meta:
        model = Booking
        fields = ('resident', 'start', 'end')
