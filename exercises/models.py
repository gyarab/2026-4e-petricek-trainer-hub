from django.conf import settings
from django.db import models


class Exercise(models.Model):
    class Category(models.TextChoices):
        STRENGTH = "STRENGTH", "Síla"
        CARDIO = "CARDIO", "Kardio"
        MOBILITY = "MOBILITY", "Mobilita"

    class TrackingType(models.TextChoices):
        SETS_REPS_WEIGHT = "SETS_REPS_WEIGHT", "Série, opakování a váha"
        SETS_REPS = "SETS_REPS", "Série a opakování (s vlastní vahou)"
        TIME = "TIME", "Čas"
        DISTANCE_TIME = "DISTANCE_TIME", "Vzdálenost a čas"

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=20, choices=Category.choices)
    muscle_group = models.CharField(max_length=50, blank=True)
    tracking_type = models.CharField(max_length=20, choices=TrackingType.choices)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="created_exercises",
    )

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name
