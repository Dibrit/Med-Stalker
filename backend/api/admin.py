from django.contrib import admin

from .models import Appointment, Diagnosis, DoctorProfile, PatientProfile, Prescription

admin.site.site_header = "Med-Stalker administration"
admin.site.site_title = "Med-Stalker"


class DiagnosisInline(admin.TabularInline):
    """Read-only snapshot of diagnoses on the patient change page."""

    model = Diagnosis
    extra = 0
    can_delete = False
    show_change_link = True
    fields = ("title", "icd_code", "status", "recorded_by", "diagnosed_at")
    readonly_fields = fields
    ordering = ("-diagnosed_at",)

    def has_add_permission(self, request, obj=None):
        return False


class PrescriptionInline(admin.TabularInline):
    """Read-only snapshot of prescriptions on the patient change page."""

    model = Prescription
    extra = 0
    can_delete = False
    show_change_link = True
    fields = ("medication_name", "diagnosis", "prescribed_by", "issued_at", "valid_until")
    readonly_fields = fields
    ordering = ("-issued_at",)

    def has_add_permission(self, request, obj=None):
        return False


class AppointmentInline(admin.TabularInline):
    """Read-only snapshot of appointments on the patient change page."""

    model = Appointment
    extra = 0
    can_delete = False
    show_change_link = True
    fields = ("doctor", "status", "starts_at", "ends_at", "reason")
    readonly_fields = fields
    ordering = ("starts_at",)

    def has_add_permission(self, request, obj=None):
        return False


class RecordedDiagnosisInline(admin.TabularInline):
    """Diagnoses recorded by this doctor (read-only; edit via Diagnosis admin)."""

    model = Diagnosis
    fk_name = "recorded_by"
    verbose_name_plural = "Diagnoses recorded by this doctor"
    extra = 0
    can_delete = False
    show_change_link = True
    fields = ("title", "patient", "status", "diagnosed_at")
    readonly_fields = fields
    ordering = ("-diagnosed_at",)

    def has_add_permission(self, request, obj=None):
        return False


class DoctorAppointmentInline(admin.TabularInline):
    """Appointments assigned to this doctor (read-only)."""

    model = Appointment
    fk_name = "doctor"
    verbose_name_plural = "Appointments assigned to this doctor"
    extra = 0
    can_delete = False
    show_change_link = True
    fields = ("patient", "status", "starts_at", "ends_at", "reason")
    readonly_fields = fields
    ordering = ("starts_at",)

    def has_add_permission(self, request, obj=None):
        return False


class PrescriptionForDiagnosisInline(admin.TabularInline):
    model = Prescription
    fk_name = "diagnosis"
    extra = 0
    can_delete = False
    show_change_link = True
    fields = ("medication_name", "patient", "prescribed_by", "issued_at")
    readonly_fields = fields
    ordering = ("-issued_at",)

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(DoctorProfile)
class DoctorProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "specialization", "license_number", "created_at")
    list_filter = ("created_at",)
    search_fields = ("user__username", "user__email", "license_number", "specialization")
    autocomplete_fields = ("user",)
    readonly_fields = ("created_at", "updated_at")
    list_select_related = ("user",)
    ordering = ("user__username",)
    inlines = (RecordedDiagnosisInline, DoctorAppointmentInline)
    fieldsets = (
        (None, {"fields": ("user",)}),
        ("Professional", {"fields": ("specialization", "license_number")}),
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
    )


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
    list_select_related = ("user",)
    ordering = ("user__username",)
    inlines = (DiagnosisInline, PrescriptionInline, AppointmentInline)
    fieldsets = (
        (None, {"fields": ("user",)}),
        ("Demographics", {"fields": ("date_of_birth", "phone", "medical_record_number")}),
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
    )


@admin.register(Diagnosis)
class DiagnosisAdmin(admin.ModelAdmin):
    list_display = ("title", "patient", "recorded_by", "status", "diagnosed_at")
    list_filter = (
        "status",
        ("recorded_by", admin.RelatedOnlyFieldListFilter),
        "diagnosed_at",
    )
    search_fields = (
        "title",
        "description",
        "icd_code",
        "patient__user__username",
        "recorded_by__user__username",
    )
    autocomplete_fields = ("patient", "recorded_by")
    readonly_fields = ("created_at", "updated_at")
    date_hierarchy = "diagnosed_at"
    list_select_related = ("patient", "patient__user", "recorded_by", "recorded_by__user")
    ordering = ("-diagnosed_at", "-pk")
    inlines = (PrescriptionForDiagnosisInline,)
    fieldsets = (
        (None, {"fields": ("patient", "recorded_by")}),
        ("Clinical", {"fields": ("title", "description", "icd_code", "status", "diagnosed_at")}),
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
    )


@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = (
        "medication_name_or_label",
        "patient",
        "prescribed_by",
        "diagnosis",
        "issued_at",
        "valid_until",
    )
    list_filter = (
        "issued_at",
        ("diagnosis", admin.RelatedOnlyFieldListFilter),
    )
    search_fields = (
        "medication_name",
        "instructions",
        "patient__user__username",
        "prescribed_by__user__username",
    )
    autocomplete_fields = ("patient", "prescribed_by", "diagnosis")
    readonly_fields = ("created_at", "updated_at")
    date_hierarchy = "issued_at"
    list_select_related = (
        "patient",
        "patient__user",
        "prescribed_by",
        "prescribed_by__user",
        "diagnosis",
    )
    ordering = ("-issued_at", "-pk")
    fieldsets = (
        (None, {"fields": ("patient", "prescribed_by", "diagnosis")}),
        ("Order", {"fields": ("medication_name", "instructions", "issued_at", "valid_until")}),
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
    )

    @admin.display(description="Medication / label")
    def medication_name_or_label(self, obj: Prescription) -> str:
        return obj.medication_name or "Recommendation"


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ("starts_at", "ends_at", "status", "patient", "doctor")
    list_filter = (
        "status",
        "starts_at",
        ("doctor", admin.RelatedOnlyFieldListFilter),
    )
    search_fields = (
        "reason",
        "patient__user__username",
        "doctor__user__username",
    )
    autocomplete_fields = ("patient", "doctor")
    readonly_fields = ("created_at", "updated_at")
    date_hierarchy = "starts_at"
    list_select_related = ("patient", "patient__user", "doctor", "doctor__user")
    ordering = ("starts_at", "pk")
    fieldsets = (
        (None, {"fields": ("patient", "doctor", "status")}),
        ("Schedule", {"fields": ("starts_at", "ends_at", "reason")}),
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
    )
