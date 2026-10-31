from django import forms
from django.db.models import Q

from accounts.models import ClientProfile
from exercises.models import Exercise

from .models import PlanDay, PlanExercise, TrainingPlan


class PlanForm(forms.ModelForm):
    class Meta:
        model = TrainingPlan
        fields = ("name", "client", "start_date", "is_active")
        labels = {
            "name": "Název plánu",
            "client": "Klient",
            "start_date": "Začátek",
            "is_active": "Aktivní",
        }
        widgets = {
            "start_date": forms.DateInput(format="%Y-%m-%d", attrs={"type": "date"}),
        }

    def __init__(self, *args, trainer, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["client"].queryset = ClientProfile.objects.filter(
            trainer=trainer
        ).select_related("user")
        self.fields["client"].label_from_instance = lambda profile: str(profile.user)


class PlanDayForm(forms.ModelForm):
    class Meta:
        model = PlanDay
        fields = ("name",)
        labels = {"name": "Název dne"}


class PlanExerciseForm(forms.ModelForm):
    class Meta:
        model = PlanExercise
        fields = (
            "exercise",
            "target_sets",
            "target_reps",
            "target_weight",
            "target_seconds",
            "note",
        )
        labels = {
            "exercise": "Cvik",
            "target_sets": "Počet sérií",
            "target_reps": "Opakování",
            "target_weight": "Hmotnost (kg)",
            "target_seconds": "Čas (sekundy)",
            "note": "Poznámka",
        }

    def __init__(self, *args, trainer, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["exercise"].queryset = Exercise.objects.filter(
            Q(created_by__isnull=True) | Q(created_by=trainer)
        )

    def clean(self):
        cleaned = super().clean()
        exercise = cleaned.get("exercise")
        if exercise is None:
            return cleaned

        required_by_type = {
            Exercise.TrackingType.SETS_REPS_WEIGHT: (
                "target_sets",
                "target_reps",
                "target_weight",
            ),
                Exercise.TrackingType.REPS_OPT_WEIGHT: ("target_sets", "target_reps"),
                Exercise.TrackingType.SETS_REPS: ("target_sets", "target_reps"),
            Exercise.TrackingType.TIME: ("target_seconds",),
            Exercise.TrackingType.DISTANCE_TIME: ("target_seconds",),
        }
        for field in required_by_type.get(exercise.tracking_type, ()):
            if cleaned.get(field) in (None, ""):
                self.add_error(field, "Toto pole je pro vybraný cvik povinné.")
        return cleaned
