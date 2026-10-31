from django.conf import settings
from django.db import models

from exercises.models import Exercise


class TrainingPlan(models.Model):
    name = models.CharField(max_length=100)
    trainer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="plans_created",
    )
    client = models.ForeignKey(
        "accounts.ClientProfile",
        on_delete=models.CASCADE,
        related_name="plans",
    )
    start_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} ({self.client.user})"


class PlanDay(models.Model):
    plan = models.ForeignKey(TrainingPlan, on_delete=models.CASCADE, related_name="days")
    order = models.PositiveSmallIntegerField(default=1)
    name = models.CharField(max_length=100)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return f"{self.plan.name} - {self.name}"


class PlanExercise(models.Model):
    day = models.ForeignKey(PlanDay, on_delete=models.CASCADE, related_name="items")
    exercise = models.ForeignKey(
        Exercise,
        on_delete=models.PROTECT,
        related_name="plan_items",
    )
    order = models.PositiveSmallIntegerField(default=1)
    target_sets = models.PositiveSmallIntegerField(null=True, blank=True)
    target_reps = models.PositiveSmallIntegerField(null=True, blank=True)
    target_weight = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    target_seconds = models.PositiveIntegerField(null=True, blank=True)
    note = models.CharField(max_length=200, blank=True)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return f"{self.exercise} in {self.day}"
