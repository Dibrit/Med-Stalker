from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from .factories import create_doctor_user

User = get_user_model()


class AuthLoginTests(APITestCase):
    def setUp(self):
        self.user = create_doctor_user(username="login_doc", password="good-password")

    def test_login_returns_tokens(self):
        response = self.client.post(
            "/api/auth/login/",
            {"username": "login_doc", "password": "good-password"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_login_rejects_invalid_password(self):
        response = self.client.post(
            "/api/auth/login/",
            {"username": "login_doc", "password": "wrong"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class AuthRefreshTests(APITestCase):
    def setUp(self):
        self.user = create_doctor_user(username="refresh_doc", password="pw")

    def test_refresh_returns_new_access(self):
        refresh = RefreshToken.for_user(self.user)
        response = self.client.post(
            "/api/auth/refresh/",
            {"refresh": str(refresh)},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)


class AuthLogoutTests(APITestCase):
    def setUp(self):
        self.user = create_doctor_user(username="logout_doc", password="pw")

    def test_logout_blacklists_refresh_token(self):
        refresh = RefreshToken.for_user(self.user)
        access = str(refresh.access_token)
        response = self.client.post(
            "/api/auth/logout/",
            {"refresh": str(refresh)},
            format="json",
            HTTP_AUTHORIZATION=f"Bearer {access}",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        refresh_response = self.client.post(
            "/api/auth/refresh/",
            {"refresh": str(refresh)},
            format="json",
        )
        self.assertEqual(refresh_response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_logout_requires_authentication(self):
        refresh = RefreshToken.for_user(self.user)
        response = self.client.post(
            "/api/auth/logout/",
            {"refresh": str(refresh)},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_logout_rejects_invalid_refresh(self):
        refresh = RefreshToken.for_user(self.user)
        access = str(refresh.access_token)
        response = self.client.post(
            "/api/auth/logout/",
            {"refresh": "not-a-jwt"},
            format="json",
            HTTP_AUTHORIZATION=f"Bearer {access}",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class RoleGateTests(APITestCase):
    def test_user_without_profile_cannot_access_patients(self):
        user = User.objects.create_user(username="plain", password="pw")
        refresh = RefreshToken.for_user(user)
        access = str(refresh.access_token)

        response = self.client.get(
            "/api/patients/",
            HTTP_AUTHORIZATION=f"Bearer {access}",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
