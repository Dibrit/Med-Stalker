from datetime import timedelta

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from api.models import Diagnosis

from .factories import create_appointment, create_diagnosis, create_doctor_user, create_patient_user


class DiagnosisManagerTests(TestCase):
    def setUp(self):
        self.doctor = create_doctor_user(username="mgr_doc", password="pw")
        self.patient = create_patient_user(username="mgr_pat", password="pw")
        self.active = create_diagnosis(
            patient=self.patient.patient_profile,
            doctor=self.doctor.doctor_profile,
            status=Diagnosis.Status.ACTIVE,
        )
        self.resolved = create_diagnosis(
            patient=self.patient.patient_profile,
            doctor=self.doctor.doctor_profile,
            title="Old",
            status=Diagnosis.Status.RESOLVED,
        )

    def test_active_manager_filters_non_active(self):
        """Diagnosis manager.active() returns only diagnoses with active status."""
        qs = Diagnosis.objects.active()
        self.assertEqual(list(qs.order_by("pk")), [self.active])


class AppointmentValidationTests(TestCase):
    def setUp(self):
        self.doctor = create_doctor_user(username="appt_doc", password="pw")
        self.patient = create_patient_user(username="appt_pat", password="pw")
        self.other_patient = create_patient_user(username="appt_pat_two", password="pw")

    def test_requested_appointments_cannot_overlap_for_same_doctor(self):
        """Appointment model validation blocks overlapping active bookings for one doctor."""
        starts_at = timezone.now() + timedelta(days=1)
        create_appointment(
            patient=self.patient.patient_profile,
            doctor=self.doctor.doctor_profile,
            starts_at=starts_at,
            ends_at=starts_at + timedelta(minutes=45),
        )

        with self.assertRaises(ValidationError):
            create_appointment(
                patient=self.other_patient.patient_profile,
                doctor=self.doctor.doctor_profile,
                starts_at=starts_at + timedelta(minutes=15),
                ends_at=starts_at + timedelta(minutes=60),
            )
