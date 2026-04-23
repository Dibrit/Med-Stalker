from datetime import timedelta

from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from api.models import Appointment

from .factories import create_appointment, create_doctor_user, create_patient_user


class AppointmentListCreateTests(APITestCase):
    def setUp(self):
        self.doctor = create_doctor_user(username="appt_doc_1", password="pw")
        self.other_doctor = create_doctor_user(username="appt_doc_2", password="pw")
        self.patient = create_patient_user(username="appt_patient_1", password="pw")
        self.other_patient = create_patient_user(username="appt_patient_2", password="pw")

    def _auth(self, user):
        token = RefreshToken.for_user(user)
        return {"HTTP_AUTHORIZATION": f"Bearer {str(token.access_token)}"}

    def _slot(self, *, days=2, hour=10):
        starts_at = (timezone.now() + timedelta(days=days)).replace(
            hour=hour,
            minute=0,
            second=0,
            microsecond=0,
        )
        while starts_at.weekday() > 4:
            starts_at += timedelta(days=1)
        return starts_at, starts_at + timedelta(minutes=45)

    def test_patient_lists_only_own_appointments(self):
        """Patients only see appointments booked for their own profile."""
        starts_at, ends_at = self._slot(days=2, hour=10)
        create_appointment(
            patient=self.patient.patient_profile,
            doctor=self.doctor.doctor_profile,
            starts_at=starts_at,
            ends_at=ends_at,
        )
        create_appointment(
            patient=self.other_patient.patient_profile,
            doctor=self.doctor.doctor_profile,
            starts_at=starts_at + timedelta(hours=2),
            ends_at=ends_at + timedelta(hours=2),
        )

        response = self.client.get("/api/appointments/", **self._auth(self.patient))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["patient"]["id"], self.patient.patient_profile.pk)

    def test_doctor_lists_only_assigned_appointments(self):
        """Doctors only see appointments assigned to their own doctor profile."""
        starts_at, ends_at = self._slot(days=3, hour=11)
        create_appointment(
            patient=self.patient.patient_profile,
            doctor=self.doctor.doctor_profile,
            starts_at=starts_at,
            ends_at=ends_at,
        )
        create_appointment(
            patient=self.patient.patient_profile,
            doctor=self.other_doctor.doctor_profile,
            starts_at=starts_at + timedelta(hours=2),
            ends_at=ends_at + timedelta(hours=2),
        )

        response = self.client.get("/api/appointments/", **self._auth(self.doctor))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["doctor"]["id"], self.doctor.doctor_profile.pk)

    def test_patient_can_create_appointment_with_selected_doctor(self):
        """Patients can book an appointment by choosing a doctor id."""
        starts_at, ends_at = self._slot(days=4, hour=9)
        payload = {
            "doctor_id": self.doctor.doctor_profile.pk,
            "reason": "Recurring headaches",
            "starts_at": starts_at.isoformat(),
            "ends_at": ends_at.isoformat(),
        }

        response = self.client.post(
            "/api/appointments/",
            payload,
            format="json",
            **self._auth(self.patient),
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["status"], Appointment.Status.REQUESTED)
        self.assertEqual(response.data["doctor"]["id"], self.doctor.doctor_profile.pk)
        self.assertEqual(response.data["patient"]["id"], self.patient.patient_profile.pk)

    def test_doctor_cannot_create_appointment(self):
        """Only patients can book appointments through the API."""
        starts_at, ends_at = self._slot(days=5, hour=14)
        payload = {
            "doctor_id": self.other_doctor.doctor_profile.pk,
            "starts_at": starts_at.isoformat(),
            "ends_at": ends_at.isoformat(),
        }

        response = self.client.post(
            "/api/appointments/",
            payload,
            format="json",
            **self._auth(self.doctor),
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_rejects_past_start_time(self):
        """New appointments must be scheduled in the future."""
        starts_at = timezone.now() - timedelta(hours=2)
        payload = {
            "doctor_id": self.doctor.doctor_profile.pk,
            "starts_at": starts_at.isoformat(),
            "ends_at": (starts_at + timedelta(minutes=45)).isoformat(),
        }

        response = self.client.post(
            "/api/appointments/",
            payload,
            format="json",
            **self._auth(self.patient),
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("starts_at", response.data)

    def test_create_rejects_end_before_start(self):
        """Appointments must have an end time after the start time."""
        starts_at, _ = self._slot(days=6, hour=15)
        payload = {
            "doctor_id": self.doctor.doctor_profile.pk,
            "starts_at": starts_at.isoformat(),
            "ends_at": (starts_at - timedelta(minutes=15)).isoformat(),
        }

        response = self.client.post(
            "/api/appointments/",
            payload,
            format="json",
            **self._auth(self.patient),
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("ends_at", response.data)

    def test_create_rejects_doctor_time_conflict(self):
        """A patient cannot book a doctor into an overlapping active time slot."""
        starts_at, ends_at = self._slot(days=7, hour=10)
        create_appointment(
            patient=self.other_patient.patient_profile,
            doctor=self.doctor.doctor_profile,
            starts_at=starts_at,
            ends_at=ends_at,
        )
        payload = {
            "doctor_id": self.doctor.doctor_profile.pk,
            "starts_at": (starts_at + timedelta(minutes=15)).isoformat(),
            "ends_at": (ends_at + timedelta(minutes=15)).isoformat(),
        }

        response = self.client.post(
            "/api/appointments/",
            payload,
            format="json",
            **self._auth(self.patient),
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("doctor_id", response.data)

    def test_create_rejects_patient_time_conflict(self):
        """A patient cannot create overlapping active appointments for themselves."""
        starts_at, ends_at = self._slot(days=8, hour=9)
        create_appointment(
            patient=self.patient.patient_profile,
            doctor=self.doctor.doctor_profile,
            starts_at=starts_at,
            ends_at=ends_at,
        )
        payload = {
            "doctor_id": self.other_doctor.doctor_profile.pk,
            "starts_at": (starts_at + timedelta(minutes=10)).isoformat(),
            "ends_at": (ends_at + timedelta(minutes=10)).isoformat(),
        }

        response = self.client.post(
            "/api/appointments/",
            payload,
            format="json",
            **self._auth(self.patient),
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("patient", response.data)

    def test_create_rejects_non_requested_initial_status(self):
        """Clients cannot skip straight to confirmed or completed on create."""
        starts_at, ends_at = self._slot(days=9, hour=13)
        payload = {
            "doctor_id": self.doctor.doctor_profile.pk,
            "status": Appointment.Status.CONFIRMED,
            "starts_at": starts_at.isoformat(),
            "ends_at": ends_at.isoformat(),
        }

        response = self.client.post(
            "/api/appointments/",
            payload,
            format="json",
            **self._auth(self.patient),
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("status", response.data)

    def test_create_rejects_weekend_time(self):
        """Appointments can only be booked on workdays."""
        starts_at = timezone.now() + timedelta(days=1)
        while starts_at.weekday() != 5:
            starts_at += timedelta(days=1)
        starts_at = starts_at.replace(hour=10, minute=0, second=0, microsecond=0)
        payload = {
            "doctor_id": self.doctor.doctor_profile.pk,
            "starts_at": starts_at.isoformat(),
            "ends_at": (starts_at + timedelta(minutes=45)).isoformat(),
        }

        response = self.client.post(
            "/api/appointments/",
            payload,
            format="json",
            **self._auth(self.patient),
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("starts_at", response.data)

    def test_create_rejects_outside_business_hours(self):
        """Appointments must stay inside the 08:00-18:00 window."""
        starts_at, _ = self._slot(days=10, hour=7)
        payload = {
            "doctor_id": self.doctor.doctor_profile.pk,
            "starts_at": starts_at.isoformat(),
            "ends_at": (starts_at + timedelta(minutes=45)).isoformat(),
        }

        response = self.client.post(
            "/api/appointments/",
            payload,
            format="json",
            **self._auth(self.patient),
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("starts_at", response.data)


class AppointmentDetailTests(APITestCase):
    def setUp(self):
        self.doctor = create_doctor_user(username="appt_detail_doc", password="pw")
        self.other_doctor = create_doctor_user(username="appt_detail_doc_two", password="pw")
        self.patient = create_patient_user(username="appt_detail_patient", password="pw")
        self.other_patient = create_patient_user(username="appt_detail_patient_two", password="pw")
        starts_at = (timezone.now() + timedelta(days=2)).replace(
            hour=10,
            minute=0,
            second=0,
            microsecond=0,
        )
        while starts_at.weekday() > 4:
            starts_at += timedelta(days=1)
        self.appointment = create_appointment(
            patient=self.patient.patient_profile,
            doctor=self.doctor.doctor_profile,
            status=Appointment.Status.REQUESTED,
            starts_at=starts_at,
            ends_at=starts_at + timedelta(minutes=45),
        )

    def _auth(self, user):
        token = RefreshToken.for_user(user)
        return {"HTTP_AUTHORIZATION": f"Bearer {str(token.access_token)}"}

    def test_patient_can_retrieve_own_appointment(self):
        """Patients can retrieve their own booked appointment."""
        url = f"/api/appointments/{self.appointment.pk}/"
        response = self.client.get(url, **self._auth(self.patient))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_doctor_can_retrieve_assigned_appointment(self):
        """Doctors can retrieve appointments assigned to them."""
        url = f"/api/appointments/{self.appointment.pk}/"
        response = self.client.get(url, **self._auth(self.doctor))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_patient_cannot_retrieve_other_patient_appointment(self):
        """Patients cannot access appointments that belong to somebody else."""
        url = f"/api/appointments/{self.appointment.pk}/"
        response = self.client.get(url, **self._auth(self.other_patient))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_doctor_cannot_retrieve_other_doctors_appointment(self):
        """Doctors cannot access appointments assigned to a different doctor."""
        url = f"/api/appointments/{self.appointment.pk}/"
        response = self.client.get(url, **self._auth(self.other_doctor))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_patient_can_cancel_own_appointment(self):
        """Patients can cancel their own future appointments."""
        url = f"/api/appointments/{self.appointment.pk}/"
        response = self.client.patch(
            url,
            {"status": Appointment.Status.CANCELLED},
            format="json",
            **self._auth(self.patient),
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.appointment.refresh_from_db()
        self.assertEqual(self.appointment.status, Appointment.Status.CANCELLED)

    def test_patient_cannot_confirm_own_appointment(self):
        """Patients cannot mark appointments confirmed or completed."""
        url = f"/api/appointments/{self.appointment.pk}/"
        response = self.client.patch(
            url,
            {"status": Appointment.Status.CONFIRMED},
            format="json",
            **self._auth(self.patient),
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("status", response.data)

    def test_doctor_can_confirm_assigned_appointment(self):
        """Doctors can update the status of their assigned appointments."""
        url = f"/api/appointments/{self.appointment.pk}/"
        response = self.client.patch(
            url,
            {"status": Appointment.Status.CONFIRMED},
            format="json",
            **self._auth(self.doctor),
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.appointment.refresh_from_db()
        self.assertEqual(self.appointment.status, Appointment.Status.CONFIRMED)

    def test_patient_cannot_update_closed_appointment(self):
        """Patients cannot edit an appointment after it has been cancelled or completed."""
        self.appointment.status = Appointment.Status.CANCELLED
        self.appointment.save()

        url = f"/api/appointments/{self.appointment.pk}/"
        response = self.client.patch(
            url,
            {"reason": "Trying to reopen"},
            format="json",
            **self._auth(self.patient),
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_doctor_can_complete_past_appointment(self):
        """Doctors can mark a past appointment completed without resubmitting its schedule."""
        starts_at = (timezone.now() - timedelta(days=1)).replace(
            hour=10,
            minute=0,
            second=0,
            microsecond=0,
        )
        while starts_at.weekday() > 4:
            starts_at -= timedelta(days=1)
        appointment = create_appointment(
            patient=self.patient.patient_profile,
            doctor=self.doctor.doctor_profile,
            status=Appointment.Status.CONFIRMED,
            starts_at=starts_at,
            ends_at=starts_at + timedelta(minutes=45),
        )

        url = f"/api/appointments/{appointment.pk}/"
        response = self.client.patch(
            url,
            {"status": Appointment.Status.COMPLETED},
            format="json",
            **self._auth(self.doctor),
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        appointment.refresh_from_db()
        self.assertEqual(appointment.status, Appointment.Status.COMPLETED)
