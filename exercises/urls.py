from django.urls import path

from . import views

urlpatterns = [
    path("", views.exercise_list, name="exercise_list"),
    path("new/", views.exercise_create, name="exercise_create"),
    path("<int:pk>/edit/", views.exercise_edit, name="exercise_edit"),
]
