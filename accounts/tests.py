from django.test import TestCase
from django.urls import reverse

from .models import ClientProfile, User


class AccountFlowTests(TestCase):
    def test_registration_creates_profile_and_logs_user_in(self):
        response = self.client.post(
            reverse("register"),
            {
                "username": "newclient",
                "email": "client@example.com",
                "first_name": "New",
                "last_name": "Client",
                "password1": "A-very-long-test-password-928!",
                "password2": "A-very-long-test-password-928!",
            },
        )

        user = User.objects.get(username="newclient")
        self.assertRedirects(response, reverse("home"))
        self.assertEqual(self.client.session["_auth_user_id"], str(user.pk))
        self.assertTrue(ClientProfile.objects.filter(user=user).exists())

    def test_login_redirects_to_home(self):
        User.objects.create_user(username="client", password="test-password")

        response = self.client.post(
            reverse("login"),
            {"username": "client", "password": "test-password"},
        )

        self.assertRedirects(response, reverse("home"))
        self.assertIn("_auth_user_id", self.client.session)

    def test_clients_page_requires_trainer(self):
        user = User.objects.create_user(username="client", password="test-password")
        self.client.force_login(user)

        response = self.client.get(reverse("clients"))

        self.assertEqual(response.status_code, 403)

    def test_trainer_sees_assigned_clients(self):
        trainer = User.objects.create_user(
            username="trainer", password="test-password", is_trainer=True
        )
        client = User.objects.create_user(username="client", password="test-password")
        ClientProfile.objects.filter(user=client).update(trainer=trainer)
        self.client.force_login(trainer)

        response = self.client.get(reverse("clients"))

        self.assertContains(response, "client")

    def test_logout_requires_post(self):
        user = User.objects.create_user(username="client", password="test-password")
        self.client.force_login(user)

        self.assertEqual(self.client.get(reverse("logout")).status_code, 405)
        response = self.client.post(reverse("logout"))

        self.assertRedirects(response, reverse("login"))
        self.assertNotIn("_auth_user_id", self.client.session)