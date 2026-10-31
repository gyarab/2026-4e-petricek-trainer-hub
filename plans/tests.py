from django.test import TestCase
from django.urls import reverse

from accounts.models import User
from exercises.models import Exercise

from .forms import PlanExerciseForm, PlanForm
from .models import PlanDay, PlanExercise, TrainingPlan


class MyPlanTests(TestCase):
    def test_my_plan_requires_authentication(self):
        response = self.client.get(reverse("my_plan"))

        self.assertRedirects(response, f"{reverse('login')}?next={reverse('my_plan')}")

    def test_authenticated_user_sees_plan_placeholder(self):
        user = User.objects.create_user(username="client", password="test-password")
        self.client.force_login(user)

        response = self.client.get(reverse("my_plan"))

        self.assertContains(response, "Zatím nemáš žádného trenéra ani plán.")


class PlanManagementTests(TestCase):
    def setUp(self):
        self.trainer = User.objects.create_user(
            username="trainer",
            password="test-password",
            is_trainer=True,
        )
        self.other_trainer = User.objects.create_user(
            username="other-trainer",
            password="test-password",
            is_trainer=True,
        )
        self.client_user = User.objects.create_user(
            username="client",
            password="test-password",
        )
        self.client_profile = self.client_user.client_profile
        self.client_profile.trainer = self.trainer
        self.client_profile.save()
        self.global_exercise = Exercise.objects.create(
            name="Bench press",
            category=Exercise.Category.STRENGTH,
            tracking_type=Exercise.TrackingType.SETS_REPS_WEIGHT,
        )
        self.optional_weight_exercise = Exercise.objects.create(
            name="Pull-up",
            category=Exercise.Category.STRENGTH,
            tracking_type=Exercise.TrackingType.REPS_OPT_WEIGHT,
        )
        self.other_exercise = Exercise.objects.create(
            name="Run",
            category=Exercise.Category.CARDIO,
            tracking_type=Exercise.TrackingType.DISTANCE_TIME,
            created_by=self.other_trainer,
        )
        self.client.force_login(self.trainer)

    def test_trainer_plan_navigation_and_list_are_scoped_to_trainer(self):
        own_plan = TrainingPlan.objects.create(
            name="Strength",
            trainer=self.trainer,
            client=self.client_profile,
        )
        other_client = User.objects.create_user(
            username="other-client",
            password="test-password",
        )
        other_plan = TrainingPlan.objects.create(
            name="Private plan",
            trainer=self.other_trainer,
            client=other_client.client_profile,
        )

        home_response = self.client.get(reverse("home"))
        list_response = self.client.get(reverse("plan_list"))

        self.assertContains(home_response, reverse("plan_list"))
        self.assertContains(home_response, "Moje plány")
        self.assertContains(list_response, own_plan.name)
        self.assertNotContains(list_response, other_plan.name)

    def test_plan_form_only_offers_clients_assigned_to_trainer(self):
        other_client = User.objects.create_user(
            username="other-client",
            password="test-password",
        )

        form = PlanForm(trainer=self.trainer)

        self.assertQuerySetEqual(
            form.fields["client"].queryset,
            [self.client_profile],
        )
        self.assertNotIn(
            other_client.client_profile.pk,
            form.fields["client"].queryset.values_list("pk", flat=True),
        )

    def test_trainer_can_create_plan_day_and_validated_exercise(self):
        create_response = self.client.post(
            reverse("plan_create"),
            {
                "name": "Strength",
                "client": self.client_profile.pk,
                "start_date": "",
                "is_active": "on",
            },
        )
        plan = TrainingPlan.objects.get(name="Strength")
        self.assertRedirects(
            create_response,
            reverse("plan_detail", args=[plan.pk]),
        )

        day_response = self.client.post(
            reverse("plan_detail", args=[plan.pk]),
            {"name": "Day A"},
        )
        day = PlanDay.objects.get(plan=plan)
        self.assertRedirects(
            day_response,
            reverse("plan_detail", args=[plan.pk]),
        )

        invalid_response = self.client.post(
            reverse("plan_exercise_add", args=[day.pk]),
            {
                "exercise": self.global_exercise.pk,
                "target_sets": "3",
                "target_reps": "8",
                "target_weight": "",
                "target_seconds": "",
                "note": "",
            },
        )
        self.assertContains(invalid_response, "Toto pole je pro vybraný cvik povinné.")
        self.assertFalse(PlanExercise.objects.filter(day=day).exists())

        valid_response = self.client.post(
            reverse("plan_exercise_add", args=[day.pk]),
            {
                "exercise": self.global_exercise.pk,
                "target_sets": "3",
                "target_reps": "8",
                "target_weight": "62.50",
                "target_seconds": "",
                "note": "Controlled tempo",
            },
        )
        item = PlanExercise.objects.get(day=day)
        self.assertRedirects(
            valid_response,
            reverse("plan_detail", args=[plan.pk]),
        )
        self.assertEqual(item.target_weight, 62.50)

    def test_optional_weight_exercise_accepts_bodyweight_and_weighted_sets(self):
        bodyweight_form = PlanExerciseForm(
            {
                "exercise": self.optional_weight_exercise.pk,
                "target_sets": "3",
                "target_reps": "8",
                "target_weight": "",
                "target_seconds": "",
                "note": "",
            },
            trainer=self.trainer,
        )
        self.assertTrue(bodyweight_form.is_valid(), bodyweight_form.errors)
        self.assertIsNone(bodyweight_form.cleaned_data["target_weight"])

        weighted_form = PlanExerciseForm(
            {
                "exercise": self.optional_weight_exercise.pk,
                "target_sets": "3",
                "target_reps": "8",
                "target_weight": "20",
                "target_seconds": "",
                "note": "",
            },
            trainer=self.trainer,
        )
        self.assertTrue(weighted_form.is_valid(), weighted_form.errors)
        self.assertEqual(weighted_form.cleaned_data["target_weight"], 20)

        missing_sets_form = PlanExerciseForm(
            {
                "exercise": self.optional_weight_exercise.pk,
                "target_sets": "",
                "target_reps": "8",
                "target_weight": "",
                "target_seconds": "",
                "note": "",
            },
            trainer=self.trainer,
        )
        self.assertFalse(missing_sets_form.is_valid())
        self.assertIn("target_sets", missing_sets_form.errors)

    def test_trainer_cannot_assign_foreign_exercise_or_access_another_plan(self):
        other_client = User.objects.create_user(
            username="other-client",
            password="test-password",
        )
        other_plan = TrainingPlan.objects.create(
            name="Private plan",
            trainer=self.other_trainer,
            client=other_client.client_profile,
        )
        self.assertEqual(
            self.client.get(reverse("plan_detail", args=[other_plan.pk])).status_code,
            404,
        )

        own_plan = TrainingPlan.objects.create(
            name="Strength",
            trainer=self.trainer,
            client=self.client_profile,
        )
        day = PlanDay.objects.create(plan=own_plan, name="Day A")
        response = self.client.post(
            reverse("plan_exercise_add", args=[day.pk]),
            {
                "exercise": self.other_exercise.pk,
                "target_seconds": "60",
            },
        )

        self.assertContains(response, "Vyberte platnou možnost")
        self.assertFalse(PlanExercise.objects.filter(day=day).exists())

    def test_exercise_removal_requires_post_and_is_scoped_to_plan_owner(self):
        plan = TrainingPlan.objects.create(
            name="Strength",
            trainer=self.trainer,
            client=self.client_profile,
        )
        day = PlanDay.objects.create(plan=plan, name="Day A")
        item = PlanExercise.objects.create(
            day=day,
            exercise=self.global_exercise,
            target_sets=3,
            target_reps=8,
            target_weight="62.50",
        )

        self.assertEqual(
            self.client.get(reverse("plan_exercise_delete", args=[item.pk])).status_code,
            405,
        )
        response = self.client.post(reverse("plan_exercise_delete", args=[item.pk]))

        self.assertRedirects(response, reverse("plan_detail", args=[plan.pk]))
        self.assertFalse(PlanExercise.objects.filter(pk=item.pk).exists())


class ClientPlanDisplayTests(TestCase):
    def test_client_sees_only_own_active_plans_and_exercises(self):
        client_user = User.objects.create_user(
            username="client",
            password="test-password",
        )
        other_client = User.objects.create_user(
            username="other-client",
            password="test-password",
        )
        trainer = User.objects.create_user(
            username="trainer",
            password="test-password",
            is_trainer=True,
        )
        active_plan = TrainingPlan.objects.create(
            name="Active plan",
            trainer=trainer,
            client=client_user.client_profile,
        )
        inactive_plan = TrainingPlan.objects.create(
            name="Inactive plan",
            trainer=trainer,
            client=client_user.client_profile,
            is_active=False,
        )
        other_plan = TrainingPlan.objects.create(
            name="Other user's plan",
            trainer=trainer,
            client=other_client.client_profile,
        )
        day = PlanDay.objects.create(plan=active_plan, name="Day A")
        exercise = Exercise.objects.create(
            name="Bodyweight squat",
            category=Exercise.Category.STRENGTH,
            tracking_type=Exercise.TrackingType.REPS_OPT_WEIGHT,
        )
        PlanExercise.objects.create(
            day=day,
            exercise=exercise,
            target_sets=3,
            target_reps=10,
        )
        self.client.force_login(client_user)

        response = self.client.get(reverse("my_plan"))

        self.assertContains(response, active_plan.name)
        self.assertContains(response, day.name)
        self.assertContains(response, exercise.name)
        self.assertNotContains(response, inactive_plan.name)
        self.assertNotContains(response, other_plan.name)
        self.assertNotContains(response, "plan_exercise_delete")

    def test_trainer_sees_a_plan_assigned_to_their_own_profile(self):
        trainer = User.objects.create_user(
            username="trainer",
            password="test-password",
            is_trainer=True,
        )
        plan = TrainingPlan.objects.create(
            name="Trainer plan",
            trainer=trainer,
            client=trainer.client_profile,
        )
        self.client.force_login(trainer)

        plan_response = self.client.get(reverse("my_plan"))
        home_response = self.client.get(reverse("home"))

        self.assertContains(plan_response, plan.name)
        self.assertContains(plan_response, reverse("my_plan"))
        self.assertContains(home_response, reverse("my_plan"))
        self.assertContains(home_response, "Můj plán")

    def test_missing_profile_is_created_and_empty_state_uses_trainer_context(self):
        client_user = User.objects.create_user(
            username="client",
            password="test-password",
        )
        trainer = User.objects.create_user(
            username="trainer",
            password="test-password",
            is_trainer=True,
        )
        client_user.client_profile.delete()
        self.client.force_login(client_user)

        response = self.client.get(reverse("my_plan"))

        self.assertContains(response, "Zatím nemáš žádného trenéra ani plán.")
        profile = client_user.__class__.objects.get(pk=client_user.pk).client_profile
        self.assertIsNotNone(profile)
        profile.trainer = trainer
        profile.save()

        response = self.client.get(reverse("my_plan"))

        self.assertContains(response, "Zatím nemáš žádný aktivní plán.")
        self.assertContains(response, "trainer")