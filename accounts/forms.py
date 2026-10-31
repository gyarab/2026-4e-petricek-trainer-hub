from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import ClientProfile, User


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email", "first_name", "last_name")


class AddClientForm(forms.Form):
    username = forms.CharField(max_length=150, label="Uživatelské jméno klienta")

    def __init__(self, *args, trainer, **kwargs):
        super().__init__(*args, **kwargs)
        self.trainer = trainer
        self.profile = None

    def clean_username(self):
        username = self.cleaned_data["username"].strip()
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise forms.ValidationError("Uživatel s tímto jménem neexistuje.")

        profile, _ = ClientProfile.objects.get_or_create(user=user)
        if profile.trainer_id == self.trainer.id:
            raise forms.ValidationError("Tento klient už je ve vašem seznamu.")
        if profile.trainer_id is not None:
            raise forms.ValidationError("Tento uživatel už má jiného trenéra.")

        self.profile = profile
        return username