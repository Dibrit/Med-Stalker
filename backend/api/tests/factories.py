from django.contrib.auth import get_user_model
from django.utils import timezone

from api.models import Diagnosis, DoctorProfile, PatientProfile, Prescription

User = get_user_model()


def create_doctor_user(*, username="doctor", password="secret123", **user_kwargs):
    user = User.objects.create_user(username=username, password=password, **user_kwargs)
    DoctorProfile.objects.create(user=user)
    user.refresh_from_db()
    return user


def create_patient_user(*, username="patient", password="secret123", **user_kwargs):
    user = User.objects.create_user(username=username, password=password, **user_kwargs)
    PatientProfile.objects.create(user=user)
    user.refresh_from_db()
    return user


def create_diagnosis(*, patient: PatientProfile, doctor: DoctorProfile, **kwargs):
    defaults = {
        "title": "Test condition",
        "description": "",
        "diagnosed_at": timezone.now(),
        "status": Diagnosis.Status.ACTIVE,
    }
    defaults.update(kwargs)
    return Diagnosis.objects.create(patient=patient, recorded_by=doctor, **defaults)


def create_prescription(*, patient: PatientProfile, doctor: DoctorProfile, **kwargs):
    defaults = {
        "instructions": "Take as directed.",
        "issued_at": timezone.now(),
    }
    defaults.update(kwargs)
    return Prescription.objects.create(patient=patient, prescribed_by=doctor, **defaults)
