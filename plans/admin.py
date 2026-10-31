from django.contrib import admin

from .models import PlanDay, PlanExercise, TrainingPlan

admin.site.register(TrainingPlan)
admin.site.register(PlanDay)
admin.site.register(PlanExercise)
