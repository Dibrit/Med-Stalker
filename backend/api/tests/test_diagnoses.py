from datetime import timedelta

from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from api.models import Diagnosis

from .factories import create_diagnosis, create_doctor_user, create_patient_user


class DiagnosisListCreateTests(APITestCase):
    def setUp(self):
        self.doctor = create_doctor_user(username="dx_doc", password="pw")
        self.other_doctor = create_doctor_user(username="dx_other_doc", password="pw")
        self.patient = create_patient_user(username="dx_pat", password="pw")
        self.diagnosis = create_diagnosis(
            patient=self.patient.patient_profile,
            doctor=self.doctor.doctor_profile,
            title="Flu",
        )

    def _auth(self, user):
        token = RefreshToken.for_user(user)
        return {"HTTP_AUTHORIZATION": f"Bearer {str(token.access_token)}"}

    def test_doctor_lists_only_own_diagnoses(self):
        """Doctors only see diagnoses recorded by their own doctor profile."""
        extra_patient = create_patient_user(username="dx_second_pat", password="pw")
        create_diagnosis(
            patient=extra_patient.patient_profile,
            doctor=self.doctor.doctor_profile,
            title="Cold",
        )
        create_diagnosis(
            patient=self.patient.patient_profile,
            doctor=self.other_doctor.doctor_profile,
            title="Other doctor's note",
        )

        response = self.client.get("/api/diagnoses/", **self._auth(self.doctor))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        titles = {row["title"] for row in response.data}
        self.assertSetEqual(titles, {"Flu", "Cold"})
        self.assertEqual(response.data[0]["recorded_by_name"], "dx_doc")

    def test_patient_lists_only_own_diagnoses(self):
        """Patients only see diagnoses linked to their own profile."""
        extra_patient = create_patient_user(username="unrelated_pat", password="pw")
        create_diagnosis(
            patient=extra_patient.patient_profile,
            doctor=self.doctor.doctor_profile,
            title="Other",
        )

        response = self.client.get("/api/diagnoses/", **self._auth(self.patient))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["title"], "Flu")

    def test_patient_cannot_create_diagnosis(self):
        """Patients cannot create diagnoses through the API."""
        payload = {
            "patient_id": self.patient.patient_profile.pk,
            "title": "Self diagnosis",
            "description": "",
            "icd_code": "",
            "status": Diagnosis.Status.ACTIVE,
            "diagnosed_at": timezone.now().isoformat(),
        }
        response = self.client.post("/api/diagnoses/", payload, format="json", **self._auth(self.patient))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_doctor_can_create_diagnosis(self):
        """Doctors can create diagnoses and are recorded as the author automatically."""
        payload = {
            "patient_id": self.patient.patient_profile.pk,
            "title": "New",
            "description": "note",
            "icd_code": "A00",
            "status": Diagnosis.Status.CHRONIC,
            "diagnosed_at": timezone.now().isoformat(),
        }
        response = self.client.post("/api/diagnoses/", payload, format="json", **self._auth(self.doctor))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["title"], "New")
        self.assertEqual(response.data["recorded_by_id"], self.doctor.doctor_profile.pk)

    def test_doctor_cannot_create_future_diagnosis(self):
        """Diagnosis creation rejects diagnosed_at values in the future."""
        payload = {
            "patient_id": self.patient.patient_profile.pk,
            "title": "Future diagnosis",
            "description": "note",
            "icd_code": "A00",
            "status": Diagnosis.Status.ACTIVE,
            "diagnosed_at": (timezone.now() + timedelta(days=1)).isoformat(),
        }
        response = self.client.post("/api/diagnoses/", payload, format="json", **self._auth(self.doctor))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("diagnosed_at", response.data)


class DiagnosisDetailTests(APITestCase):
    def setUp(self):
        self.doctor = create_doctor_user(username="dxd_doc", password="pw")
        self.other_doctor = create_doctor_user(username="dxd_other_doc", password="pw")
        self.patient = create_patient_user(username="dxd_pat", password="pw")
        self.diagnosis = create_diagnosis(
            patient=self.patient.patient_profile,
            doctor=self.doctor.doctor_profile,
            title="Condition",
        )

    def _auth(self, user):
        token = RefreshToken.for_user(user)
        return {"HTTP_AUTHORIZATION": f"Bearer {str(token.access_token)}"}

    def test_patient_can_retrieve_own_diagnosis(self):
        """Patients can open a diagnosis that belongs to them."""
        url = f"/api/diagnoses/{self.diagnosis.pk}/"
        response = self.client.get(url, **self._auth(self.patient))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_doctor_cannot_retrieve_other_doctors_diagnosis(self):
        """Doctors cannot open diagnoses recorded by a different doctor."""
        foreign_diagnosis = create_diagnosis(
            patient=self.patient.patient_profile,
            doctor=self.other_doctor.doctor_profile,
            title="Outside diagnosis",
        )
        url = f"/api/diagnoses/{foreign_diagnosis.pk}/"
        response = self.client.get(url, **self._auth(self.doctor))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_patient_cannot_retrieve_other_patients_diagnosis(self):
        """Patients cannot open diagnosis details for another patient."""
        other = create_patient_user(username="other_dx_pat", password="pw")
        other_diagnosis = create_diagnosis(
            patient=other.patient_profile,
            doctor=self.doctor.doctor_profile,
            title="Private",
        )
        url = f"/api/diagnoses/{other_diagnosis.pk}/"
        response = self.client.get(url, **self._auth(self.patient))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_patient_cannot_update_diagnosis(self):
        """Patients cannot update diagnosis records."""
        url = f"/api/diagnoses/{self.diagnosis.pk}/"
        response = self.client.patch(
            url,
            {"title": "Changed"},
            format="json",
            **self._auth(self.patient),
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_doctor_can_update_diagnosis(self):
        """Doctors can partially update diagnosis records."""
        url = f"/api/diagnoses/{self.diagnosis.pk}/"
        response = self.client.patch(
            url,
            {"title": "Updated"},
            format="json",
            **self._auth(self.doctor),
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.diagnosis.refresh_from_db()
        self.assertEqual(self.diagnosis.title, "Updated")

    def test_doctor_cannot_update_other_doctors_diagnosis(self):
        """Doctors cannot update diagnoses recorded by another doctor."""
        foreign_diagnosis = create_diagnosis(
            patient=self.patient.patient_profile,
            doctor=self.other_doctor.doctor_profile,
            title="Foreign diagnosis",
        )
        url = f"/api/diagnoses/{foreign_diagnosis.pk}/"
        response = self.client.patch(
            url,
            {"title": "Blocked"},
            format="json",
            **self._auth(self.doctor),
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
