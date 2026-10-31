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

    def test_anonymous_visitor_sees_public_homepage(self):
        response = self.client.get(reverse("home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Trénuj chytře.")
        self.assertContains(response, "Sleduj progres.")
        self.assertContains(response, reverse("register"))
        self.assertContains(response, reverse("login"))

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

    def test_trainer_home_shows_exercises_and_clients_buttons(self):
        trainer = User.objects.create_user(
            username="trainer", password="test-password", is_trainer=True
        )
        self.client.force_login(trainer)

        response = self.client.get(reverse("home"))

        self.assertContains(response, reverse("exercise_list"))
        self.assertContains(response, reverse("clients"))
        self.assertContains(response, "Cviky")
        self.assertContains(response, "Klienti")

    def test_client_home_shows_exercises_and_plan_buttons(self):
        client = User.objects.create_user(username="client", password="test-password")
        self.client.force_login(client)

        response = self.client.get(reverse("home"))

        self.assertContains(response, reverse("exercise_list"))
        self.assertContains(response, reverse("my_plan"))
        self.assertContains(response, "Můj plán")

    def test_trainer_can_add_unassigned_client(self):
        trainer = User.objects.create_user(
            username="trainer", password="test-password", is_trainer=True
        )
        User.objects.create_user(username="client", password="test-password")
        self.client.force_login(trainer)

        response = self.client.post(reverse("client_add"), {"username": "client"})

        self.assertRedirects(response, reverse("clients"))
        self.assertEqual(User.objects.get(username="client").client_profile.trainer, trainer)

    def test_trainer_cannot_add_client_assigned_to_another_trainer(self):
        trainer = User.objects.create_user(
            username="trainer", password="test-password", is_trainer=True
        )
        other_trainer = User.objects.create_user(
            username="other", password="test-password", is_trainer=True
        )
        client = User.objects.create_user(username="client", password="test-password")
        ClientProfile.objects.filter(user=client).update(trainer=other_trainer)
        self.client.force_login(trainer)

        response = self.client.post(reverse("client_add"), {"username": "client"})

        self.assertContains(response, "Tento uživatel už má jiného trenéra.")
        self.assertEqual(ClientProfile.objects.get(user=client).trainer, other_trainer)

    def test_trainer_can_remove_own_client_with_post(self):
        trainer = User.objects.create_user(
            username="trainer", password="test-password", is_trainer=True
        )
        client = User.objects.create_user(username="client", password="test-password")
        profile = client.client_profile
        profile.trainer = trainer
        profile.save()
        self.client.force_login(trainer)

        response = self.client.post(reverse("client_remove", args=[profile.pk]))

        self.assertRedirects(response, reverse("clients"))
        profile.refresh_from_db()
        self.assertIsNone(profile.trainer)

    def test_trainer_cannot_remove_another_trainers_client(self):
        trainer = User.objects.create_user(
            username="trainer", password="test-password", is_trainer=True
        )
        other_trainer = User.objects.create_user(
            username="other", password="test-password", is_trainer=True
        )
        client = User.objects.create_user(username="client", password="test-password")
        profile = client.client_profile
        profile.trainer = other_trainer
        profile.save()
        self.client.force_login(trainer)

        response = self.client.post(reverse("client_remove", args=[profile.pk]))

        self.assertEqual(response.status_code, 404)
        profile.refresh_from_db()
        self.assertEqual(profile.trainer, other_trainer)

    def test_logout_requires_post(self):
        user = User.objects.create_user(username="client", password="test-password")
        self.client.force_login(user)

        self.assertEqual(self.client.get(reverse("logout")).status_code, 405)
        response = self.client.post(reverse("logout"))

        self.assertRedirects(response, reverse("login"))
        self.assertNotIn("_auth_user_id", self.client.session)