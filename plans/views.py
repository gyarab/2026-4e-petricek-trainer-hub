from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from accounts.decorators import trainer_required
from accounts.models import ClientProfile

from .forms import PlanDayForm, PlanExerciseForm, PlanForm
from .models import PlanDay, PlanExercise, TrainingPlan


@login_required
def my_plan(request):
    profile, _ = ClientProfile.objects.get_or_create(user=request.user)
    plans = (
        profile.plans.filter(is_active=True)
        .select_related("trainer")
        .prefetch_related("days__items__exercise")
    )
    return render(
        request,
        "plans/my_plan.html",
        {"plans": plans, "profile": profile},
    )


@trainer_required
def plan_list(request):
    plans = TrainingPlan.objects.filter(trainer=request.user).select_related(
        "client__user"
    )
    return render(request, "plans/list.html", {"plans": plans})


@trainer_required
def plan_create(request):
    if request.method == "POST":
        form = PlanForm(request.POST, trainer=request.user)
        if form.is_valid():
            plan = form.save(commit=False)
            plan.trainer = request.user
            plan.save()
            return redirect("plan_detail", pk=plan.pk)
    else:
        form = PlanForm(trainer=request.user)
    no_clients = not form.fields["client"].queryset.exists()
    return render(
        request,
        "plans/form.html",
        {"form": form, "no_clients": no_clients},
    )


@trainer_required
def plan_detail(request, pk):
    plan = get_object_or_404(
        TrainingPlan.objects.select_related("client__user"),
        pk=pk,
        trainer=request.user,
    )
    if request.method == "POST":
        day_form = PlanDayForm(request.POST)
        if day_form.is_valid():
            day = day_form.save(commit=False)
            day.plan = plan
            day.order = plan.days.count() + 1
            day.save()
            return redirect("plan_detail", pk=plan.pk)
    else:
        day_form = PlanDayForm()
    days = plan.days.prefetch_related("items__exercise")
    return render(
        request,
        "plans/detail.html",
        {"plan": plan, "days": days, "day_form": day_form},
    )


@trainer_required
def plan_exercise_add(request, day_pk):
    day = get_object_or_404(
        PlanDay.objects.select_related("plan__client__user"),
        pk=day_pk,
        plan__trainer=request.user,
    )
    if request.method == "POST":
        form = PlanExerciseForm(request.POST, trainer=request.user)
        if form.is_valid():
            item = form.save(commit=False)
            item.day = day
            item.order = day.items.count() + 1
            item.save()
            return redirect("plan_detail", pk=day.plan_id)
    else:
        form = PlanExerciseForm(trainer=request.user)
    return render(request, "plans/exercise_form.html", {"form": form, "day": day})


@trainer_required
@require_POST
def plan_exercise_delete(request, pk):
    item = get_object_or_404(PlanExercise, pk=pk, day__plan__trainer=request.user)
    plan_pk = item.day.plan_id
    item.delete()
    return redirect("plan_detail", pk=plan_pk)