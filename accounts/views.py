from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .decorators import trainer_required
from .forms import RegisterForm


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


@login_required
def home(request):
    return render(request, "home.html")


@trainer_required
def clients_list(request):
    clients = request.user.clients.select_related("user")
    return render(request, "accounts/clients.html", {"clients": clients})