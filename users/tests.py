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

        expected_url = reverse("login") + "?registered=1"
        self.assertRedirects(response, expected_url)
        self.assertTrue(User.objects.filter(username="alice").exists())
        self.assertTrue(ECPKey.objects.filter(user__username="alice").exists())
        self.assertIn("private_key_download", self.client.session)
        self.assertEqual(self.client.session["private_key_filename"], "alice_private_key.pem")
