from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from api.models import PatientProfile

from .factories import create_doctor_user

User = get_user_model()


class AuthRegisterTests(APITestCase):
    def test_register_creates_patient_profile_and_returns_tokens(self):
        """Patient registration creates a patient profile and returns JWT tokens."""
        payload = {
            "username": "new_patient",
            "email": "new_patient@example.com",
            "first_name": "New",
            "last_name": "Patient",
            "password": "good-password-123",
            "password_confirm": "good-password-123",
            "date_of_birth": "2001-04-15",
            "phone": "+77001234567",
        }

        response = self.client.post("/api/auth/register/", payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
        self.assertEqual(response.data["patient"]["username"], payload["username"])
        self.assertEqual(response.data["patient"]["email"], payload["email"])
        self.assertEqual(response.data["patient"]["phone"], payload["phone"])
        self.assertTrue(response.data["patient"]["medical_record_number"].startswith("MRN-"))

        user = User.objects.get(username=payload["username"])
        self.assertTrue(hasattr(user, "patient_profile"))
        self.assertFalse(hasattr(user, "doctor_profile"))
        self.assertEqual(PatientProfile.objects.count(), 1)

    def test_register_rejects_duplicate_username(self):
        """Registration fails when the requested username already exists."""
        User.objects.create_user(username="taken", email="existing@example.com", password="secret123")

        response = self.client.post(
            "/api/auth/register/",
            {
                "username": "taken",
                "email": "fresh@example.com",
                "first_name": "Test",
                "last_name": "User",
                "password": "good-password-123",
                "password_confirm": "good-password-123",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("username", response.data)

    def test_register_rejects_password_mismatch(self):
        """Registration fails when password confirmation does not match."""
        response = self.client.post(
            "/api/auth/register/",
            {
                "username": "mismatch",
                "email": "mismatch@example.com",
                "first_name": "Mis",
                "last_name": "Match",
                "password": "good-password-123",
                "password_confirm": "different-password-123",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password_confirm", response.data)

    def test_register_rejects_future_date_of_birth(self):
        """Registration fails when date of birth is set in the future."""
        response = self.client.post(
            "/api/auth/register/",
            {
                "username": "future_patient",
                "email": "future@example.com",
                "first_name": "Future",
                "last_name": "Patient",
                "password": "good-password-123",
                "password_confirm": "good-password-123",
                "date_of_birth": "2999-01-01",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("date_of_birth", response.data)


class AuthLoginTests(APITestCase):
    def setUp(self):
        self.user = create_doctor_user(username="login_doc", password="good-password")

    def test_login_returns_tokens(self):
        """Login returns access and refresh tokens for valid credentials."""
        response = self.client.post(
            "/api/auth/login/",
            {"username": "login_doc", "password": "good-password"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_login_rejects_invalid_password(self):
        """Login fails when the password is incorrect."""
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
        """Refresh endpoint exchanges a refresh token for a new access token."""
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
        """Logout blacklists the submitted refresh token."""
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
        """Logout is rejected when no access token is provided."""
        refresh = RefreshToken.for_user(self.user)
        response = self.client.post(
            "/api/auth/logout/",
            {"refresh": str(refresh)},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_logout_rejects_invalid_refresh(self):
        """Logout fails when the submitted refresh token is invalid."""
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
        """Users without a doctor or patient profile cannot open patient endpoints."""
        user = User.objects.create_user(username="plain", password="pw")
        refresh = RefreshToken.for_user(user)
        access = str(refresh.access_token)

        response = self.client.get(
            "/api/patients/",
            HTTP_AUTHORIZATION=f"Bearer {access}",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
