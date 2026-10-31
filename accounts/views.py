from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .decorators import trainer_required
from .forms import AddClientForm, RegisterForm
from .models import ClientProfile


def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("home")
    else:
        form = RegisterForm()
    return render(request, "registration/register.html", {"form": form})


def home(request):
    return render(request, "home.html")


@trainer_required
def clients_list(request):
    clients = request.user.clients.select_related("user")
    return render(request, "accounts/clients.html", {"clients": clients})


@trainer_required
def client_add(request):
    if request.method == "POST":
        form = AddClientForm(request.POST, trainer=request.user)
        if form.is_valid():
            profile = form.profile
            profile.trainer = request.user
            profile.save()
            return redirect("clients")
    else:
        form = AddClientForm(trainer=request.user)
    return render(request, "accounts/client_add.html", {"form": form})


@trainer_required
@require_POST
def client_remove(request, pk):
    profile = get_object_or_404(ClientProfile, pk=pk, trainer=request.user)
    profile.trainer = None
    profile.save()
    return redirect("clients")