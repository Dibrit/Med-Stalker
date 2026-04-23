import logging

from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Appointment, Diagnosis, DoctorProfile, PatientProfile, Prescription
from .permissions import IsDoctor, IsDoctorOrPatient, IsPatient
from .serializers import (
    AppointmentSerializer,
    DiagnosisSerializer,
    DoctorSerializer,
    LoginSerializer,
    LogoutSerializer,
    PatientSerializer,
    PatientRegistrationSerializer,
    PrescriptionSerializer,
)

logger = logging.getLogger(__name__)


@api_view(["POST"])
@permission_classes([AllowAny])
def auth_login(request):
    # Using a serializer here keeps auth validation in one place.
    serializer = LoginSerializer(data=request.data, context={"request": request})
    serializer.is_valid(raise_exception=True)
    user = serializer.validated_data["user"]
    logger.info("Login succeeded for user_id=%s", user.pk)
    refresh = RefreshToken.for_user(user)
    return Response(
        {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        },
        status=status.HTTP_200_OK,
    )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def auth_logout(request):
    serializer = LogoutSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    try:
        token = RefreshToken(serializer.validated_data["refresh"])
        token.blacklist()
    except TokenError:
        # If the refresh token is already bad/expired, we just return 400.
        # (This makes the frontend behavior predictable.)
        logger.warning(
            "Logout failed: invalid refresh token for user_id=%s",
            request.user.pk,
        )
        return Response(
            {"detail": "Invalid or expired refresh token."},
            status=status.HTTP_400_BAD_REQUEST,
        )
    logger.info("Logout succeeded for user_id=%s", request.user.pk)
    return Response({"detail": "Successfully logged out."}, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes([AllowAny])
def auth_register(request):
    serializer = PatientRegistrationSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    patient = serializer.save()
    refresh = RefreshToken.for_user(patient.user)
    logger.info(
        "Patient registration succeeded user_id=%s patient_id=%s",
        patient.user_id,
        patient.pk,
    )
    return Response(
        {
            "patient": PatientSerializer(patient).data,
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        },
        status=status.HTTP_201_CREATED,
    )


def _diagnosis_queryset_for_user(user):
    # Small helper so we don't repeat "doctor sees all / patient sees own" logic.
    qs = Diagnosis.objects.select_related(
        "patient",
        "patient__user",
        "recorded_by",
        "recorded_by__user",
    )
    if getattr(user, "doctor_profile", None):
        return qs.all()
    if getattr(user, "patient_profile", None):
        return qs.filter(patient=user.patient_profile)
    return qs.none()


class DiagnosisListCreateView(APIView):
    permission_classes = [IsAuthenticated, IsDoctorOrPatient]

    def get(self, request):
        queryset = _diagnosis_queryset_for_user(request.user)
        serializer = DiagnosisSerializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request):
        if not getattr(request.user, "doctor_profile", None):
            raise PermissionDenied("Only doctors can create diagnoses.")
        # `recorded_by` is set inside the serializer based on request.user.
        serializer = DiagnosisSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        logger.info(
            "Diagnosis created id=%s patient_id=%s by user_id=%s",
            serializer.instance.pk,
            serializer.instance.patient_id,
            request.user.pk,
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class DiagnosisDetailView(APIView):
    permission_classes = [IsAuthenticated, IsDoctorOrPatient]

    def get_object(self, pk):
        return get_object_or_404(_diagnosis_queryset_for_user(self.request.user), pk=pk)

    def get(self, request, pk):
        diagnosis = self.get_object(pk)
        serializer = DiagnosisSerializer(diagnosis)
        return Response(serializer.data)

    def put(self, request, pk):
        return self._update(request, pk, partial=False)

    def patch(self, request, pk):
        return self._update(request, pk, partial=True)

    def delete(self, request, pk):
        if not getattr(request.user, "doctor_profile", None):
            raise PermissionDenied("Only doctors can delete diagnoses.")
        diagnosis = self.get_object(pk)
        diagnosis_id = diagnosis.pk
        patient_id = diagnosis.patient_id
        diagnosis.delete()
        logger.info(
            "Diagnosis deleted id=%s patient_id=%s by user_id=%s",
            diagnosis_id,
            patient_id,
            request.user.pk,
        )
        return Response(status=status.HTTP_204_NO_CONTENT)

    def _update(self, request, pk, *, partial):
        if not getattr(request.user, "doctor_profile", None):
            raise PermissionDenied("Only doctors can update diagnoses.")
        diagnosis = self.get_object(pk)
        serializer = DiagnosisSerializer(
            diagnosis,
            data=request.data,
            partial=partial,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        logger.info(
            "Diagnosis updated id=%s partial=%s by user_id=%s",
            diagnosis.pk,
            partial,
            request.user.pk,
        )
        return Response(serializer.data)


class PatientListView(generics.ListAPIView):
    serializer_class = PatientSerializer
    permission_classes = [IsAuthenticated, IsDoctorOrPatient]

    def get_queryset(self):
        user = self.request.user
        if getattr(user, "doctor_profile", None):
            return PatientProfile.objects.select_related("user").all()
        if getattr(user, "patient_profile", None):
            return PatientProfile.objects.select_related("user").filter(pk=user.patient_profile.pk)
        return PatientProfile.objects.none()


class PatientDetailView(generics.RetrieveAPIView):
    serializer_class = PatientSerializer
    permission_classes = [IsAuthenticated, IsDoctorOrPatient]
    lookup_field = "pk"

    def get_queryset(self):
        user = self.request.user
        if getattr(user, "doctor_profile", None):
            return PatientProfile.objects.select_related("user").all()
        if getattr(user, "patient_profile", None):
            return PatientProfile.objects.select_related("user").filter(pk=user.patient_profile.pk)
        return PatientProfile.objects.none()


class DoctorListView(generics.ListAPIView):
    serializer_class = DoctorSerializer
    permission_classes = [IsAuthenticated, IsDoctorOrPatient]
    queryset = DoctorProfile.objects.select_related("user").all()


def _prescription_queryset_for_user(user):
    # Same access pattern as diagnoses.
    related = ("patient", "patient__user", "diagnosis", "prescribed_by", "prescribed_by__user")
    if getattr(user, "doctor_profile", None):
        return Prescription.objects.select_related(*related)
    if getattr(user, "patient_profile", None):
        return Prescription.objects.filter(patient=user.patient_profile).select_related(*related)
    return Prescription.objects.none()


class PrescriptionListCreateView(generics.ListCreateAPIView):
    serializer_class = PrescriptionSerializer
    permission_classes = [IsAuthenticated, IsDoctorOrPatient]

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAuthenticated(), IsDoctor()]
        return super().get_permissions()

    def get_queryset(self):
        return _prescription_queryset_for_user(self.request.user)

    def perform_create(self, serializer):
        instance = serializer.save()
        logger.info(
            "Prescription created id=%s patient_id=%s by user_id=%s",
            instance.pk,
            instance.patient_id,
            self.request.user.pk,
        )


class PrescriptionDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PrescriptionSerializer
    permission_classes = [IsAuthenticated, IsDoctorOrPatient]
    lookup_field = "pk"

    def get_permissions(self):
        if self.request.method != "GET":
            return [IsAuthenticated(), IsDoctor()]
        return super().get_permissions()

    def get_queryset(self):
        return _prescription_queryset_for_user(self.request.user)

    def perform_update(self, serializer):
        instance = serializer.save()
        logger.info(
            "Prescription updated id=%s patient_id=%s by user_id=%s",
            instance.pk,
            instance.patient_id,
            self.request.user.pk,
        )

    def perform_destroy(self, instance):
        prescription_id = instance.pk
        patient_id = instance.patient_id
        user_id = self.request.user.pk
        super().perform_destroy(instance)
        logger.info(
            "Prescription deleted id=%s patient_id=%s by user_id=%s",
            prescription_id,
            patient_id,
            user_id,
        )


def _appointment_queryset_for_user(user):
    related = ("patient", "patient__user", "doctor", "doctor__user")
    if getattr(user, "doctor_profile", None):
        return Appointment.objects.select_related(*related).filter(doctor=user.doctor_profile)
    if getattr(user, "patient_profile", None):
        return Appointment.objects.select_related(*related).filter(patient=user.patient_profile)
    return Appointment.objects.none()


class AppointmentListCreateView(generics.ListCreateAPIView):
    serializer_class = AppointmentSerializer
    permission_classes = [IsAuthenticated, IsDoctorOrPatient]

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAuthenticated(), IsPatient()]
        return super().get_permissions()

    def get_queryset(self):
        return _appointment_queryset_for_user(self.request.user)

    def perform_create(self, serializer):
        instance = serializer.save()
        logger.info(
            "Appointment created id=%s patient_id=%s doctor_id=%s by user_id=%s",
            instance.pk,
            instance.patient_id,
            instance.doctor_id,
            self.request.user.pk,
        )


class AppointmentDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = AppointmentSerializer
    permission_classes = [IsAuthenticated, IsDoctorOrPatient]
    lookup_field = "pk"

    def get_queryset(self):
        return _appointment_queryset_for_user(self.request.user)

    def perform_update(self, serializer):
        instance = serializer.save()
        logger.info(
            "Appointment updated id=%s status=%s by user_id=%s",
            instance.pk,
            instance.status,
            self.request.user.pk,
        )
