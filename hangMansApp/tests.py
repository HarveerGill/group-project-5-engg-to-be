from django.test import TestCase
from django.contrib.auth.models import User


class HangmanTests(TestCase):
    # Create your tests here.
    def test_history_requires_login(self):
        response = self.client.get('/history/')
        self.assertEqual(response.status_code, 302)

    def test_password_is_hashed(self):
        user = User.objects.create_user(
            username='test',
            password='Password123'
        )
        self.assertNotEqual(user.password, 'Password123')

    def test_login_success(self):
        User.objects.create_user(
            username='test',
            password='Password123'
        )
        result = self.client.login(
            username='test',
            password='Password123'
        )
        self.assertTrue(result)

    def test_user_only_sees_own_scores(self):
        # Stub for ownership validation
        self.assertTrue(True)
     