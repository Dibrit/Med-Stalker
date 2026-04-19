from django.contrib import admin

from .models import Diagnosis, DoctorProfile, PatientProfile, Prescription


@admin.register(DoctorProfile)
class DoctorProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "specialization", "license_number", "created_at")
    list_filter = ("created_at",)
    search_fields = ("user__username", "user__email", "license_number", "specialization")
    autocomplete_fields = ("user",)
    readonly_fields = ("created_at", "updated_at")


@admin.register(PatientProfile)
class PatientProfileAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "medical_record_number",
        "date_of_birth",
        "phone",
        "created_at",
    )
    list_filter = ("created_at",)
    search_fields = (
        "user__username",
        "user__email",
        "medical_record_number",
        "phone",
    )
    autocomplete_fields = ("user",)
    readonly_fields = ("created_at", "updated_at")


@admin.register(Diagnosis)
class DiagnosisAdmin(admin.ModelAdmin):
    list_display = ("title", "patient", "recorded_by", "status", "diagnosed_at")
    list_filter = ("status", "diagnosed_at")
    search_fields = ("title", "description", "icd_code", "patient__user__username")
    autocomplete_fields = ("patient", "recorded_by")
    readonly_fields = ("created_at", "updated_at")
    date_hierarchy = "diagnosed_at"


@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = (
        "medication_name_or_label",
        "patient",
        "prescribed_by",
        "issued_at",
        "valid_until",
    )
    list_filter = ("issued_at",)
    search_fields = (
        "medication_name",
        "instructions",
        "patient__user__username",
    )
    autocomplete_fields = ("patient", "prescribed_by", "diagnosis")
    readonly_fields = ("created_at", "updated_at")
    date_hierarchy = "issued_at"

    @admin.display(description="Medication / label")
    def medication_name_or_label(self, obj: Prescription) -> str:
        return obj.medication_name or "Recommendation"
