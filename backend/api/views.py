from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Diagnosis, PatientProfile, Prescription
from .permissions import IsDoctor, IsDoctorOrPatient
from .serializers import (
    DiagnosisSerializer,
    LoginSerializer,
    LogoutSerializer,
    PatientSerializer,
    PrescriptionSerializer,
)


@api_view(["POST"])
@permission_classes([AllowAny])
def auth_login(request):
    serializer = LoginSerializer(data=request.data, context={"request": request})
    serializer.is_valid(raise_exception=True)
    user = serializer.validated_data["user"]
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
        return Response(
            {"detail": "Invalid or expired refresh token."},
            status=status.HTTP_400_BAD_REQUEST,
        )
    return Response({"detail": "Successfully logged out."}, status=status.HTTP_200_OK)


def _diagnosis_queryset_for_user(user):
    if getattr(user, "doctor_profile", None):
        return Diagnosis.objects.all()
    if getattr(user, "patient_profile", None):
        return Diagnosis.objects.filter(patient=user.patient_profile)
    return Diagnosis.objects.none()


def _ensure_diagnosis_visible(user, diagnosis: Diagnosis) -> None:
    qs = _diagnosis_queryset_for_user(user)
    if not qs.filter(pk=diagnosis.pk).exists():
        raise PermissionDenied("You do not have access to this diagnosis.")


class DiagnosisListCreateView(APIView):
    permission_classes = [IsAuthenticated, IsDoctorOrPatient]

    def get(self, request):
        queryset = _diagnosis_queryset_for_user(request.user)
        serializer = DiagnosisSerializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request):
        if not getattr(request.user, "doctor_profile", None):
            raise PermissionDenied("Only doctors can create diagnoses.")
        serializer = DiagnosisSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class DiagnosisDetailView(APIView):
    permission_classes = [IsAuthenticated, IsDoctorOrPatient]

    def get_object(self, pk):
        diagnosis = get_object_or_404(Diagnosis, pk=pk)
        _ensure_diagnosis_visible(self.request.user, diagnosis)
        return diagnosis

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
        diagnosis.delete()
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
        return Response(serializer.data)


class PatientListView(generics.ListAPIView):
    serializer_class = PatientSerializer
    permission_classes = [IsAuthenticated, IsDoctorOrPatient]

    def get_queryset(self):
        user = self.request.user
        if getattr(user, "doctor_profile", None):
            return PatientProfile.objects.all()
        if getattr(user, "patient_profile", None):
            return PatientProfile.objects.filter(pk=user.patient_profile.pk)
        return PatientProfile.objects.none()


class PatientDetailView(generics.RetrieveAPIView):
    serializer_class = PatientSerializer
    permission_classes = [IsAuthenticated, IsDoctorOrPatient]
    lookup_field = "pk"

    def get_queryset(self):
        user = self.request.user
        if getattr(user, "doctor_profile", None):
            return PatientProfile.objects.all()
        if getattr(user, "patient_profile", None):
            return PatientProfile.objects.filter(pk=user.patient_profile.pk)
        return PatientProfile.objects.none()


def _prescription_queryset_for_user(user):
    if getattr(user, "doctor_profile", None):
        return Prescription.objects.select_related("patient", "patient__user", "diagnosis")
    if getattr(user, "patient_profile", None):
        return Prescription.objects.filter(patient=user.patient_profile).select_related(
            "patient", "patient__user", "diagnosis"
        )
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
        serializer.save()


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
