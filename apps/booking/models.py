from django.contrib.auth import get_user_model
from django.db import models

from apps.account.models import Company, BaseModel

User = get_user_model()


class Booking(BaseModel):
    resident = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="bookings")
    room = models.ForeignKey(Company, on_delete=models.SET_NULL, null=True, related_name='room_times')
    start = models.DateTimeField(null=True, blank=True)
    end = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f'The {self.room} room was booked {self.start.strftime("%Y-%m-%d %H:%M:%S")} - {self.end.strftime("%Y-%m-%d %H:%M:%S")}'
