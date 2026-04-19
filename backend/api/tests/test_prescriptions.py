from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from .factories import create_diagnosis, create_doctor_user, create_patient_user, create_prescription


class PrescriptionListCreateTests(APITestCase):
    def setUp(self):
        self.doctor = create_doctor_user(username="rx_doc", password="pw")
        self.patient = create_patient_user(username="rx_pat", password="pw")
        self.other_patient = create_patient_user(username="rx_pat2", password="pw")
        self.diagnosis = create_diagnosis(
            patient=self.patient.patient_profile,
            doctor=self.doctor.doctor_profile,
        )
        create_prescription(
            patient=self.patient.patient_profile,
            doctor=self.doctor.doctor_profile,
            diagnosis=self.diagnosis,
            medication_name="Med A",
        )
        create_prescription(
            patient=self.other_patient.patient_profile,
            doctor=self.doctor.doctor_profile,
            medication_name="Med B",
        )

    def _auth(self, user):
        token = RefreshToken.for_user(user)
        return {"HTTP_AUTHORIZATION": f"Bearer {str(token.access_token)}"}

    def test_doctor_lists_all_prescriptions(self):
        response = self.client.get("/api/prescriptions/", **self._auth(self.doctor))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        names = {row["medication_name"] for row in response.data}
        self.assertSetEqual(names, {"Med A", "Med B"})

    def test_patient_lists_only_own_prescriptions(self):
        response = self.client.get("/api/prescriptions/", **self._auth(self.patient))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["medication_name"], "Med A")

    def test_patient_cannot_create_prescription(self):
        payload = {
            "patient_id": self.patient.patient_profile.pk,
            "diagnosis": self.diagnosis.pk,
            "medication_name": "X",
            "instructions": "do it",
            "issued_at": timezone.now().isoformat(),
        }
        response = self.client.post(
            "/api/prescriptions/",
            payload,
            format="json",
            **self._auth(self.patient),
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_doctor_can_create_prescription(self):
        payload = {
            "patient_id": self.patient.patient_profile.pk,
            "diagnosis": self.diagnosis.pk,
            "medication_name": "New med",
            "instructions": "twice daily",
            "issued_at": timezone.now().isoformat(),
        }
        response = self.client.post(
            "/api/prescriptions/",
            payload,
            format="json",
            **self._auth(self.doctor),
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["prescribed_by_id"], self.doctor.doctor_profile.pk)

    def test_create_rejects_diagnosis_for_different_patient(self):
        other_dx = create_diagnosis(
            patient=self.other_patient.patient_profile,
            doctor=self.doctor.doctor_profile,
        )
        payload = {
            "patient_id": self.patient.patient_profile.pk,
            "diagnosis": other_dx.pk,
            "medication_name": "Bad link",
            "instructions": "n/a",
            "issued_at": timezone.now().isoformat(),
        }
        response = self.client.post(
            "/api/prescriptions/",
            payload,
            format="json",
            **self._auth(self.doctor),
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_rejects_valid_until_before_issued_at(self):
        payload = {
            "patient_id": self.patient.patient_profile.pk,
            "diagnosis": self.diagnosis.pk,
            "medication_name": "Bad date",
            "instructions": "n/a",
            "issued_at": timezone.now().isoformat(),
            "valid_until": "2000-01-01",
        }
        response = self.client.post(
            "/api/prescriptions/",
            payload,
            format="json",
            **self._auth(self.doctor),
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("valid_until", response.data)


class PrescriptionDetailTests(APITestCase):
    def setUp(self):
        self.doctor = create_doctor_user(username="rxd_doc", password="pw")
        self.patient = create_patient_user(username="rxd_pat", password="pw")
        self.prescription = create_prescription(
            patient=self.patient.patient_profile,
            doctor=self.doctor.doctor_profile,
            medication_name="Detail med",
        )

    def _auth(self, user):
        token = RefreshToken.for_user(user)
        return {"HTTP_AUTHORIZATION": f"Bearer {str(token.access_token)}"}

    def test_patient_can_retrieve_own_prescription(self):
        url = f"/api/prescriptions/{self.prescription.pk}/"
        response = self.client.get(url, **self._auth(self.patient))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_patient_cannot_update_prescription(self):
        url = f"/api/prescriptions/{self.prescription.pk}/"
        response = self.client.patch(
            url,
            {"instructions": "changed"},
            format="json",
            **self._auth(self.patient),
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_doctor_can_update_prescription(self):
        url = f"/api/prescriptions/{self.prescription.pk}/"
        response = self.client.patch(
            url,
            {"instructions": "updated text"},
            format="json",
            **self._auth(self.doctor),
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.prescription.refresh_from_db()
        self.assertEqual(self.prescription.instructions, "updated text")
