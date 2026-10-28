from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from accounts.decorators import trainer_required

from .forms import ExerciseForm
from .models import Exercise


@trainer_required
def exercise_list(request):
    exercises = Exercise.objects.filter(
        Q(created_by__isnull=True) | Q(created_by=request.user)
    )
    return render(request, "exercises/list.html", {"exercises": exercises})


@trainer_required
def exercise_create(request):
    if request.method == "POST":
        form = ExerciseForm(request.POST)
        if form.is_valid():
            exercise = form.save(commit=False)
            exercise.created_by = request.user
            exercise.save()
            return redirect("exercise_list")
    else:
        form = ExerciseForm()
    return render(
        request,
        "exercises/form.html",
        {"form": form, "title": "Nový cvik"},
    )


@trainer_required
def exercise_edit(request, pk):
    exercise = get_object_or_404(Exercise, pk=pk, created_by=request.user)
    if request.method == "POST":
        form = ExerciseForm(request.POST, instance=exercise)
        if form.is_valid():
            form.save()
            return redirect("exercise_list")
    else:
        form = ExerciseForm(instance=exercise)
    return render(
        request,
        "exercises/form.html",
        {"form": form, "title": "Upravit cvik"},
    )
