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

    def test_download_key_view_serves_and_clears_session(self):
        # Setup session
        session = self.client.session
        session["private_key_download"] = "fake-private-key"
        session["private_key_filename"] = "alice_private_key.pem"
        session.save()

        response = self.client.get(reverse("download_key"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode(), "fake-private-key")
        self.assertEqual(response["Content-Disposition"], 'attachment; filename="alice_private_key.pem"')

        # Verify session is cleared
        self.assertNotIn("private_key_download", self.client.session)
        self.assertNotIn("private_key_filename", self.client.session)

    def test_download_key_view_404_if_no_key(self):
        response = self.client.get(reverse("download_key"))
        self.assertEqual(response.status_code, 404)
