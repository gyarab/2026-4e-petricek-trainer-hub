from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Uživatel systému. Dědí z AbstractUser (username, heslo, email, ...).

    Role nejsou vzájemně výlučné: každý uživatel může trénovat (jako klient)
    a zároveň může být trenér (is_trainer=True), který spravuje další klienty.
    """

    is_trainer = models.BooleanField(default=False, verbose_name="Trenér")

    def __str__(self):
        return self.get_full_name() or self.username
class ClientProfile(models.Model):
    """Training profile of a user. Every user has exactly one, because
    every user can train (a trainer can train himself too)."""

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="client_profile",
    )
    trainer = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="clients",
    )
    birth_date = models.DateField(null=True, blank=True)
    height_cm = models.PositiveSmallIntegerField(null=True, blank=True)
    note = models.TextField(blank=True)

    def __str__(self):
        return f"Profile of {self.user}"