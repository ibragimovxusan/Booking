from django.contrib import admin
from .models import User

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ["id", "username", "email", "role", "is_active", "is_staff", "is_superuser"]
    list_display_links = ["id", "username"]