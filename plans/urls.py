from django.urls import path

from . import views

urlpatterns = [
    path("", views.plan_list, name="plan_list"),
    path("new/", views.plan_create, name="plan_create"),
    path("<int:pk>/", views.plan_detail, name="plan_detail"),
    path(
        "day/<int:day_pk>/add-exercise/",
        views.plan_exercise_add,
        name="plan_exercise_add",
    ),
    path(
        "item/<int:pk>/delete/",
        views.plan_exercise_delete,
        name="plan_exercise_delete",
    ),
    path("my/", views.my_plan, name="my_plan"),
]