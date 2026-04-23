from rest_framework.permissions import BasePermission


def _has_doctor_profile(user) -> bool:
    # "Role" in this project = the user has a related profile row.
    return bool(getattr(user, "doctor_profile", None))


def _has_patient_profile(user) -> bool:
    return bool(getattr(user, "patient_profile", None))


class IsDoctor(BasePermission):
    message = "Doctor role required."

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and _has_doctor_profile(request.user))


class IsPatient(BasePermission):
    message = "Patient role required."

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and _has_patient_profile(request.user))


class IsDoctorOrPatient(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        # Both roles can read their allowed data; write ops are gated in views.
        return _has_doctor_profile(request.user) or _has_patient_profile(request.user)
