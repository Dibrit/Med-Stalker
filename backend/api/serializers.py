import logging
from secrets import token_hex

from django.contrib.auth import authenticate, get_user_model, password_validation
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction
from django.utils import timezone
from rest_framework import serializers

from .models import Diagnosis, PatientProfile, Prescription

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
