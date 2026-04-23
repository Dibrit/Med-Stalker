from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from .factories import create_doctor_user, create_patient_user


class DoctorListTests(APITestCase):
    def setUp(self):
        self.doctor_a = create_doctor_user(
            username="doctor_alpha",
            password="pw",
            first_name="Alice",
            last_name="Ng",
        )
        self.doctor_b = create_doctor_user(
            username="doctor_beta",
            password="pw",
            first_name="Boris",
            last_name="Kim",
        )
        self.patient = create_patient_user(username="doctor_list_patient", password="pw")

    def _auth(self, user):
        token = RefreshToken.for_user(user)
        return {"HTTP_AUTHORIZATION": f"Bearer {str(token.access_token)}"}

    def test_patient_can_list_doctors(self):
        """Patients can load the doctor directory when booking an appointment."""
        response = self.client.get("/api/doctors/", **self._auth(self.patient))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ids = {row["id"] for row in response.data}
        self.assertSetEqual(ids, {self.doctor_a.doctor_profile.pk, self.doctor_b.doctor_profile.pk})

    def test_doctor_can_list_doctors(self):
        """Doctors can also view the doctor directory."""
        response = self.client.get("/api/doctors/", **self._auth(self.doctor_a))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
