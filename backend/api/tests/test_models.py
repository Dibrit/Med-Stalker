from django.test import TestCase

from api.models import Diagnosis

from .factories import create_diagnosis, create_doctor_user, create_patient_user


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
        qs = Diagnosis.objects.active()
        self.assertEqual(list(qs.order_by("pk")), [self.active])
