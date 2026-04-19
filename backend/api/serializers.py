from django.contrib.auth import authenticate
from rest_framework import serializers

from .models import Diagnosis, PatientProfile, Prescription


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True, style={"input_type": "password"})

    def validate(self, attrs):
        user = authenticate(
            request=self.context.get("request"),
            username=attrs["username"],
            password=attrs["password"],
        )
        if user is None:
            raise serializers.ValidationError("Invalid username or password.")
        if not user.is_active:
            raise serializers.ValidationError("User account is disabled.")
        attrs["user"] = user
        return attrs


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField(write_only=True)


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

    class Meta:
        model = Diagnosis
        fields = (
            "id",
            "patient",
            "patient_id",
            "recorded_by_id",
            "title",
            "description",
            "icd_code",
            "status",
            "diagnosed_at",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "patient", "recorded_by_id", "created_at", "updated_at")

    def create(self, validated_data):
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

    class Meta:
        model = Prescription
        fields = (
            "id",
            "patient",
            "patient_id",
            "prescribed_by_id",
            "diagnosis",
            "medication_name",
            "instructions",
            "issued_at",
            "valid_until",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "patient", "prescribed_by_id", "created_at", "updated_at")

    def validate(self, attrs):
        diagnosis = attrs.get("diagnosis")
        patient = attrs.get("patient")
        if self.partial:
            if patient is None and self.instance is not None:
                patient = self.instance.patient
            if diagnosis is None and self.instance is not None:
                diagnosis = self.instance.diagnosis
        if diagnosis and patient and diagnosis.patient_id != patient.pk:
            raise serializers.ValidationError(
                {"diagnosis": "Diagnosis must belong to the selected patient."}
            )
        return attrs

    def create(self, validated_data):
        request = self.context["request"]
        validated_data["prescribed_by"] = request.user.doctor_profile
        return super().create(validated_data)
