from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class DoctorProfile(models.Model):
    """Extra fields for users that are doctors."""

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="doctor_profile",
    )
    specialization = models.CharField(max_length=255, blank=True)
    license_number = models.CharField(max_length=64, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["user__username"]

    def __str__(self) -> str:
        return f"Doctor: {self.user.get_username()}"


class PatientProfile(models.Model):
    """Extra fields for users that are patients."""

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="patient_profile",
    )
    date_of_birth = models.DateField(null=True, blank=True)
    phone = models.CharField(max_length=32, blank=True)
    medical_record_number = models.CharField(
        max_length=64,
        unique=True,
        null=True,
        blank=True,
        help_text=_("Optional clinic-specific patient identifier."),
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["user__username"]

    def __str__(self) -> str:
        return f"Patient: {self.user.get_username()}"


class DiagnosisQuerySet(models.QuerySet):
    def active(self):
        return self.filter(status=Diagnosis.Status.ACTIVE)


class DiagnosisManager(models.Manager):
    def get_queryset(self):
        return DiagnosisQuerySet(self.model, using=self._db)

    def active(self):
        return self.get_queryset().active()


class Diagnosis(models.Model):
    """A diagnosis entry (doctor -> patient)."""

    class Status(models.TextChoices):
        ACTIVE = "active", _("Active")
        RESOLVED = "resolved", _("Resolved")
        CHRONIC = "chronic", _("Chronic")

    patient = models.ForeignKey(
        PatientProfile,
        on_delete=models.CASCADE,
        related_name="diagnoses",
    )
    recorded_by = models.ForeignKey(
        DoctorProfile,
        on_delete=models.PROTECT,
        related_name="recorded_diagnoses",
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    icd_code = models.CharField(
        max_length=32,
        blank=True,
        help_text=_("Optional ICD or similar coding system identifier."),
    )
    status = models.CharField(
        max_length=16,
        choices=Status.choices,
        default=Status.ACTIVE,
    )
    diagnosed_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = DiagnosisManager()

    class Meta:
        ordering = ["-diagnosed_at", "-pk"]
        verbose_name_plural = "diagnoses"
        indexes = [
            models.Index(fields=["patient", "-diagnosed_at"]),
            models.Index(fields=["recorded_by", "-diagnosed_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.title} ({self.patient})"


class Prescription(models.Model):
    """Prescription / recommendation (optionally linked to a diagnosis)."""

    patient = models.ForeignKey(
        PatientProfile,
        on_delete=models.CASCADE,
        related_name="prescriptions",
    )
    prescribed_by = models.ForeignKey(
        DoctorProfile,
        on_delete=models.PROTECT,
        related_name="prescriptions_written",
    )
    diagnosis = models.ForeignKey(
        Diagnosis,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="prescriptions",
    )
    medication_name = models.CharField(max_length=255, blank=True)
    instructions = models.TextField(
        help_text=_("Dosage, schedule, lifestyle recommendation, or other instructions."),
    )
    issued_at = models.DateTimeField()
    valid_until = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-issued_at", "-pk"]
        indexes = [
            models.Index(fields=["patient", "-issued_at"]),
            models.Index(fields=["prescribed_by", "-issued_at"]),
        ]

    def __str__(self) -> str:
        label = self.medication_name or _("Recommendation")
        return f"{label} → {self.patient}"


class Appointment(models.Model):
    """A booked visit between a patient and a doctor."""

    class Status(models.TextChoices):
        REQUESTED = "requested", _("Requested")
        CONFIRMED = "confirmed", _("Confirmed")
        CANCELLED = "cancelled", _("Cancelled")
        COMPLETED = "completed", _("Completed")

    patient = models.ForeignKey(
        PatientProfile,
        on_delete=models.CASCADE,
        related_name="appointments",
    )
    doctor = models.ForeignKey(
        DoctorProfile,
        on_delete=models.PROTECT,
        related_name="appointments",
    )
    status = models.CharField(
        max_length=16,
        choices=Status.choices,
        default=Status.REQUESTED,
    )
    reason = models.TextField(
        blank=True,
        help_text=_("Optional description of symptoms or the reason for the visit."),
    )
    starts_at = models.DateTimeField()
    ends_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["starts_at", "pk"]
        indexes = [
            models.Index(fields=["doctor", "starts_at"]),
            models.Index(fields=["patient", "starts_at"]),
            models.Index(fields=["status", "starts_at"]),
        ]

    @classmethod
    def blocking_statuses(cls) -> tuple[str, str]:
        return (cls.Status.REQUESTED, cls.Status.CONFIRMED)

    def clean(self):
        errors = {}

        if self.starts_at and self.ends_at and self.ends_at <= self.starts_at:
            errors["ends_at"] = _("Appointment end must be after its start.")

        if (
            self.patient_id
            and self.doctor_id
            and self.starts_at
            and self.ends_at
            and self.status in self.blocking_statuses()
        ):
            overlapping = Appointment.objects.filter(
                status__in=self.blocking_statuses(),
                starts_at__lt=self.ends_at,
                ends_at__gt=self.starts_at,
            ).exclude(pk=self.pk)
            if overlapping.filter(doctor_id=self.doctor_id).exists():
                errors["doctor"] = _(
                    "The selected doctor already has an appointment during that time."
                )
            if overlapping.filter(patient_id=self.patient_id).exists():
                errors["patient"] = _(
                    "The patient already has an appointment during that time."
                )

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.patient} with {self.doctor} at {self.starts_at:%Y-%m-%d %H:%M}"
