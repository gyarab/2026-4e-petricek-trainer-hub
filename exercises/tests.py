from django.test import TestCase
from django.urls import reverse

from accounts.models import User

from .models import Exercise


class ExerciseViewsTests(TestCase):
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
        self.global_exercise = Exercise.objects.create(
            name="Bench press",
            category=Exercise.Category.STRENGTH,
            tracking_type=Exercise.TrackingType.SETS_REPS_WEIGHT,
        )
        self.own_exercise = Exercise.objects.create(
            name="Squat",
            category=Exercise.Category.STRENGTH,
            tracking_type=Exercise.TrackingType.SETS_REPS,
            created_by=self.trainer,
        )
        self.other_exercise = Exercise.objects.create(
            name="Run",
            category=Exercise.Category.CARDIO,
            tracking_type=Exercise.TrackingType.DISTANCE_TIME,
            created_by=self.other_trainer,
        )

    def test_exercise_pages_require_trainer(self):
        response = self.client.get(reverse("exercise_list"))
        self.assertRedirects(
            response,
            f"{reverse('login')}?next={reverse('exercise_list')}",
        )

        self.client.force_login(self.client_user)
        response = self.client.get(reverse("exercise_list"))
        self.assertEqual(response.status_code, 403)

    def test_trainer_sees_global_and_own_exercises_only(self):
        self.client.force_login(self.trainer)

        response = self.client.get(reverse("exercise_list"))

        self.assertContains(response, self.global_exercise.name)
        self.assertContains(response, self.own_exercise.name)
        self.assertNotContains(response, self.other_exercise.name)
        self.assertContains(
            response,
            reverse("exercise_edit", args=[self.own_exercise.pk]),
        )
        self.assertNotContains(
            response,
            reverse("exercise_edit", args=[self.global_exercise.pk]),
        )

    def test_trainer_can_create_only_an_exercise_owned_by_them(self):
        self.client.force_login(self.trainer)

        response = self.client.post(
            reverse("exercise_create"),
            {
                "name": "Plank",
                "description": "",
                "category": Exercise.Category.STRENGTH,
                "muscle_group": "core",
                "tracking_type": Exercise.TrackingType.TIME,
                "created_by": self.other_trainer.pk,
            },
        )

        exercise = Exercise.objects.get(name="Plank")
        self.assertRedirects(response, reverse("exercise_list"))
        self.assertEqual(exercise.created_by, self.trainer)

    def test_trainer_can_edit_own_exercise_but_not_global_or_other_trainers(self):
        self.client.force_login(self.trainer)

        response = self.client.post(
            reverse("exercise_edit", args=[self.own_exercise.pk]),
            {
                "name": "Front squat",
                "description": "",
                "category": Exercise.Category.STRENGTH,
                "muscle_group": "legs",
                "tracking_type": Exercise.TrackingType.SETS_REPS,
            },
        )

        self.assertRedirects(response, reverse("exercise_list"))
        self.own_exercise.refresh_from_db()
        self.assertEqual(self.own_exercise.name, "Front squat")

        for exercise in (self.global_exercise, self.other_exercise):
            with self.subTest(exercise=exercise.name):
                response = self.client.get(
                    reverse("exercise_edit", args=[exercise.pk])
                )
                self.assertEqual(response.status_code, 404)
