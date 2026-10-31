from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("register/", views.register, name="register"),
    path("login/", auth_views.LoginView.as_view(), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("clients/", views.clients_list, name="clients"),
    path("clients/add/", views.client_add, name="client_add"),
    path("clients/<int:pk>/remove/", views.client_remove, name="client_remove"),
]