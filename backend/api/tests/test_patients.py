from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from .factories import create_doctor_user, create_patient_user


class PatientListTests(APITestCase):
    def setUp(self):
        self.doctor = create_doctor_user(username="d1", password="pw")
        self.patient_a = create_patient_user(username="p1", password="pw")
        self.patient_b = create_patient_user(username="p2", password="pw")

    def _auth(self, user):
        token = RefreshToken.for_user(user)
        return {"HTTP_AUTHORIZATION": f"Bearer {str(token.access_token)}"}

    def test_doctor_sees_all_patients(self):
        """Doctors can list all patient profiles."""
        response = self.client.get("/api/patients/", **self._auth(self.doctor))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ids = {row["id"] for row in response.data}
        self.assertSetEqual(ids, {self.patient_a.patient_profile.pk, self.patient_b.patient_profile.pk})

    def test_patient_sees_only_self(self):
        """Patients only see their own profile in the patient list endpoint."""
        response = self.client.get("/api/patients/", **self._auth(self.patient_a))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], self.patient_a.patient_profile.pk)


class PatientDetailTests(APITestCase):
    def setUp(self):
        self.doctor = create_doctor_user(username="doc2", password="pw")
        self.patient = create_patient_user(username="pat2", password="pw")
        self.other = create_patient_user(username="pat3", password="pw")

    def _auth(self, user):
        token = RefreshToken.for_user(user)
        return {"HTTP_AUTHORIZATION": f"Bearer {str(token.access_token)}"}

    def test_doctor_can_open_any_patient(self):
        """Doctors can retrieve the detail page for any patient."""
        url = f"/api/patients/{self.other.patient_profile.pk}/"
        response = self.client.get(url, **self._auth(self.doctor))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.other.patient_profile.pk)

    def test_patient_cannot_open_other_patient(self):
        """Patients cannot retrieve another patient's detail page."""
        url = f"/api/patients/{self.other.patient_profile.pk}/"
        response = self.client.get(url, **self._auth(self.patient))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
