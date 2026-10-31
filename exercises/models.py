import re

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

YOUTUBE_ID = re.compile(
    r"(?:youtube\.com/(?:watch\?v=|shorts/|embed/)|youtu\.be/)([A-Za-z0-9_-]{11})"
)


class Exercise(models.Model):
    class Category(models.TextChoices):
        STRENGTH = "STRENGTH", "Síla"
        CARDIO = "CARDIO", "Kardio"
        MOBILITY = "MOBILITY", "Mobilita"

    class TrackingType(models.TextChoices):
        SETS_REPS_WEIGHT = "SETS_REPS_WEIGHT", "Série, opakování a váha"
        REPS_OPT_WEIGHT = "REPS_OPT_WEIGHT", "Série, opakování a volitelná váha"
        SETS_REPS = "SETS_REPS", "Série a opakování (s vlastní vahou)"
        TIME = "TIME", "Čas"
        DISTANCE_TIME = "DISTANCE_TIME", "Vzdálenost a čas"

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=20, choices=Category.choices)
    muscle_group = models.CharField(max_length=50, blank=True)
    tracking_type = models.CharField(max_length=20, choices=TrackingType.choices)
    video_url = models.URLField(blank=True)
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

    @property
    def video_embed_url(self):
        match = YOUTUBE_ID.search(self.video_url)
        if match:
            return f"https://www.youtube-nocookie.com/embed/{match.group(1)}"
        return ""

    def clean(self):
        if self.video_url and not YOUTUBE_ID.search(self.video_url):
            raise ValidationError({"video_url": "Zadejte odkaz na YouTube video."})
