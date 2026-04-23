import logging
from secrets import token_hex

from django.contrib.auth import authenticate, get_user_model, password_validation
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction
from django.utils import timezone
from rest_framework import serializers

from .models import Appointment, Diagnosis, DoctorProfile, PatientProfile, Prescription

logger = logging.getLogger(__name__)
User = get_user_model()


def _display_name_for_user(user) -> str:
    full_name = user.get_full_name().strip()
    return full_name or user.get_username()


def _generate_medical_record_number() -> str:
    while True:
        candidate = f"MRN-{token_hex(4).upper()}"
        if not PatientProfile.objects.filter(medical_record_number=candidate).exists():
            return candidate


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True, style={"input_type": "password"})

    def validate(self, attrs):
        # `authenticate` uses Django's auth backend(s).
        user = authenticate(
            request=self.context.get("request"),
            username=attrs["username"],
            password=attrs["password"],
        )
        if user is None:
            logger.warning("Login failed: invalid credentials for username=%r", attrs["username"])
            raise serializers.ValidationError("Invalid username or password.")
        if not user.is_active:
            logger.warning(
                "Login failed: inactive user username=%r user_id=%s",
                attrs["username"],
                user.pk,
            )
            raise serializers.ValidationError("User account is disabled.")
        attrs["user"] = user
        return attrs


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField(write_only=True)


class PatientRegistrationSerializer(serializers.Serializer):
    username = serializers.CharField(write_only=True, max_length=150)
    email = serializers.EmailField(write_only=True)
    first_name = serializers.CharField(write_only=True, max_length=150)
    last_name = serializers.CharField(write_only=True, max_length=150)
    password = serializers.CharField(
        write_only=True,
        style={"input_type": "password"},
        trim_whitespace=False,
    )
    password_confirm = serializers.CharField(
        write_only=True,
        style={"input_type": "password"},
        trim_whitespace=False,
    )
    date_of_birth = serializers.DateField(required=False, allow_null=True)
    phone = serializers.CharField(required=False, allow_blank=True, max_length=32)

    def validate_username(self, value):
        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError("A user with that username already exists.")
        return value

    def validate_email(self, value):
        normalized = User.objects.normalize_email(value)
        if User.objects.filter(email__iexact=normalized).exists():
            raise serializers.ValidationError("A user with that email already exists.")
        return normalized

    def validate_date_of_birth(self, value):
        if value and value > timezone.localdate():
            raise serializers.ValidationError("Date of birth cannot be in the future.")
        return value

    def validate(self, attrs):
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError({"password_confirm": "Passwords do not match."})

        user = User(
            username=attrs["username"],
            email=attrs["email"],
            first_name=attrs["first_name"],
            last_name=attrs["last_name"],
        )
        try:
            password_validation.validate_password(attrs["password"], user=user)
        except DjangoValidationError as exc:
            raise serializers.ValidationError({"password": list(exc.messages)}) from exc
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        password = validated_data.pop("password")
        validated_data.pop("password_confirm")
        phone = validated_data.pop("phone", "")
        date_of_birth = validated_data.pop("date_of_birth", None)

        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
            password=password,
        )
        return PatientProfile.objects.create(
            user=user,
            phone=phone,
            date_of_birth=date_of_birth,
            medical_record_number=_generate_medical_record_number(),
        )


class PatientSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)
    first_name = serializers.CharField(source="user.first_name", read_only=True)
    last_name = serializers.CharField(source="user.last_name", read_only=True)

    class Meta:
        model = PatientProfile
        fields = (
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "date_of_birth",
            "phone",
            "medical_record_number",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")


class DoctorSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)
    first_name = serializers.CharField(source="user.first_name", read_only=True)
    last_name = serializers.CharField(source="user.last_name", read_only=True)
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = DoctorProfile
        fields = (
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "full_name",
            "specialization",
            "license_number",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields

    def get_full_name(self, obj: DoctorProfile) -> str:
        return obj.user.get_full_name() or obj.user.get_username()


class DiagnosisSerializer(serializers.ModelSerializer):
    patient = PatientSerializer(read_only=True)
    patient_id = serializers.PrimaryKeyRelatedField(
        queryset=PatientProfile.objects.all(),
        source="patient",
        write_only=True,
    )
    recorded_by_id = serializers.IntegerField(read_only=True)
    recorded_by_name = serializers.SerializerMethodField()

    class Meta:
        model = Diagnosis
        fields = (
            "id",
            "patient",
            "patient_id",
            "recorded_by_id",
            "recorded_by_name",
            "title",
            "description",
            "icd_code",
            "status",
            "diagnosed_at",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "patient",
            "recorded_by_id",
            "recorded_by_name",
            "created_at",
            "updated_at",
        )

    def get_recorded_by_name(self, obj):
        return _display_name_for_user(obj.recorded_by.user)

    def get_recorded_by_name(self, obj: Diagnosis) -> str:
        return obj.recorded_by.user.get_full_name() or obj.recorded_by.user.get_username()

    def validate_diagnosed_at(self, value):
        if value > timezone.now():
            raise serializers.ValidationError("Diagnosis date cannot be in the future.")
        return value

    def create(self, validated_data):
        # We don't trust the client to choose who recorded the diagnosis.
        request = self.context["request"]
        validated_data["recorded_by"] = request.user.doctor_profile
        return super().create(validated_data)


class PrescriptionSerializer(serializers.ModelSerializer):
    patient = PatientSerializer(read_only=True)
    patient_id = serializers.PrimaryKeyRelatedField(
        queryset=PatientProfile.objects.all(),
        source="patient",
        write_only=True,
    )
    diagnosis = serializers.PrimaryKeyRelatedField(
        queryset=Diagnosis.objects.all(),
        allow_null=True,
        required=False,
    )
    prescribed_by_id = serializers.IntegerField(read_only=True)
    prescribed_by_name = serializers.SerializerMethodField()

    class Meta:
        model = Prescription
        fields = (
            "id",
            "patient",
            "patient_id",
            "prescribed_by_id",
            "prescribed_by_name",
            "diagnosis",
            "medication_name",
            "instructions",
            "issued_at",
            "valid_until",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "patient",
            "prescribed_by_id",
            "prescribed_by_name",
            "created_at",
            "updated_at",
        )

    def get_prescribed_by_name(self, obj):
        return _display_name_for_user(obj.prescribed_by.user)

    def get_prescribed_by_name(self, obj: Prescription) -> str:
        return obj.prescribed_by.user.get_full_name() or obj.prescribed_by.user.get_username()

    def validate(self, attrs):
        # A couple of cross-field checks that are easier here than in the model.
        diagnosis = attrs.get("diagnosis")
        patient = attrs.get("patient")
        issued_at = attrs.get("issued_at")
        valid_until = attrs.get("valid_until")
        if self.partial:
            if patient is None and self.instance is not None:
                patient = self.instance.patient
            if diagnosis is None and self.instance is not None:
                diagnosis = self.instance.diagnosis
            if issued_at is None and self.instance is not None:
                issued_at = self.instance.issued_at
            if valid_until is None and self.instance is not None:
                valid_until = self.instance.valid_until
        if diagnosis and patient and diagnosis.patient_id != patient.pk:
            raise serializers.ValidationError(
                {"diagnosis": "Diagnosis must belong to the selected patient."}
            )
        if issued_at and valid_until and valid_until < issued_at.date():
            raise serializers.ValidationError(
                {"valid_until": "valid_until cannot be earlier than issued_at."}
            )
        return attrs

    def create(self, validated_data):
        # Same idea as diagnoses: the prescriber is the logged-in doctor.
        request = self.context["request"]
        validated_data["prescribed_by"] = request.user.doctor_profile
        return super().create(validated_data)


class AppointmentSerializer(serializers.ModelSerializer):
    patient = PatientSerializer(read_only=True)
    doctor = DoctorSerializer(read_only=True)
    doctor_id = serializers.PrimaryKeyRelatedField(
        queryset=DoctorProfile.objects.select_related("user").all(),
        source="doctor",
        write_only=True,
    )

    class Meta:
        model = Appointment
        fields = (
            "id",
            "patient",
            "doctor",
            "doctor_id",
            "status",
            "reason",
            "starts_at",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "patient", "doctor", "created_at", "updated_at")

    def validate(self, attrs):
        request = self.context["request"]
        user = request.user
        patient_profile = getattr(user, "patient_profile", None)
        doctor_profile = getattr(user, "doctor_profile", None)

        doctor = attrs.get("doctor", self.instance.doctor if self.instance else None)
        patient = self.instance.patient if self.instance else patient_profile
        starts_at = attrs.get("starts_at", self.instance.starts_at if self.instance else None)
        status_value = attrs.get(
            "status",
            self.instance.status if self.instance else Appointment.Status.REQUESTED,
        )
        starts_at_supplied = self.instance is None or "starts_at" in attrs

        if self.instance is None and patient_profile is None:
            raise serializers.ValidationError("Only patients can create appointments.")

        if self.instance is None and "status" in attrs and status_value != Appointment.Status.REQUESTED:
            raise serializers.ValidationError(
                {"status": "New appointments must start with requested status."}
            )

        if self.instance is not None and patient_profile is not None:
            if self.instance.status in (
                Appointment.Status.CANCELLED,
                Appointment.Status.COMPLETED,
            ):
                raise serializers.ValidationError("Closed appointments cannot be changed by patients.")
            if "status" in attrs and status_value not in (
                Appointment.Status.REQUESTED,
                Appointment.Status.CANCELLED,
            ):
                raise serializers.ValidationError(
                    {"status": "Patients can only keep an appointment requested or cancel it."}
                )

        if self.instance is not None and doctor_profile is not None and "doctor" in attrs:
            if attrs["doctor"].pk != self.instance.doctor_id:
                raise serializers.ValidationError(
                    {"doctor_id": "Doctors cannot reassign appointments through this endpoint."}
                )

        if (
            starts_at_supplied
            and starts_at is not None
            and starts_at <= timezone.now()
            and status_value in Appointment.blocking_statuses()
        ):
            raise serializers.ValidationError(
                {"starts_at": "Appointment must be scheduled in the future."}
            )

        if patient and doctor and starts_at:
            candidate = Appointment(
                patient=patient,
                doctor=doctor,
                status=status_value,
                reason=attrs.get("reason", self.instance.reason if self.instance else ""),
                starts_at=starts_at,
            )
            if self.instance is not None:
                candidate.pk = self.instance.pk
            try:
                candidate.clean()
            except DjangoValidationError as exc:
                detail = exc.message_dict if hasattr(exc, "message_dict") else {"detail": exc.messages}
                if "doctor" in detail:
                    detail["doctor_id"] = detail.pop("doctor")
                raise serializers.ValidationError(detail) from exc

        return attrs

    def create(self, validated_data):
        request = self.context["request"]
        validated_data["patient"] = request.user.patient_profile
        validated_data["status"] = Appointment.Status.REQUESTED
        return super().create(validated_data)
