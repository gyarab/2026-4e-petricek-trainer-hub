from django import forms

from .models import Exercise


class ExerciseForm(forms.ModelForm):
    class Meta:
        model = Exercise
        fields = (
            "name",
            "description",
            "category",
            "muscle_group",
            "tracking_type",
            "video_url",
        )
        labels = {"video_url": "Odkaz na video (YouTube)"}
