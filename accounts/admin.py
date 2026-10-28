from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import ClientProfile, User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (("Role v aplikaci", {"fields": ("is_trainer",)}),)
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Role v aplikaci", {"fields": ("is_trainer",)}),
    )
    list_display = ("username", "email", "is_trainer", "is_staff")
    list_filter = ("is_trainer", "is_staff")


@admin.register(ClientProfile)
class ClientProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "trainer", "birth_date", "height_cm")
    list_filter = ("trainer",)
