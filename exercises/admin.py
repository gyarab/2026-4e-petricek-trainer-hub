from django.contrib import admin

from .models import Exercise


@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "muscle_group", "tracking_type", "created_by")
    list_filter = ("category", "tracking_type")
    search_fields = ("name", "muscle_group")
