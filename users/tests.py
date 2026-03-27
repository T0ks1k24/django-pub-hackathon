from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from ecp_lib.models import ECPKey


class RegisterViewTests(TestCase):
    def test_register_redirects_to_login_and_stores_public_key(self):
        response = self.client.post(
            reverse("register"),
            data={
                "username": "alice",
                "password1": "VeryStrongPassword123",
                "password2": "VeryStrongPassword123",
            },
        )

        self.assertRedirects(response, reverse("login"))
        self.assertTrue(User.objects.filter(username="alice").exists())
        self.assertTrue(ECPKey.objects.filter(user__username="alice").exists())
