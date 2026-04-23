from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from . import views

urlpatterns = [
    # Auth endpoints (JWT).
    path("auth/register/", views.auth_register),
    path("auth/login/", views.auth_login),
    path("auth/logout/", views.auth_logout),
    path("auth/refresh/", TokenRefreshView.as_view()),
    # Main app endpoints.
    path("doctors/", views.DoctorListView.as_view()),
    path("patients/", views.PatientListView.as_view()),
    path("patients/<int:pk>/", views.PatientDetailView.as_view()),
    path("appointments/", views.AppointmentListCreateView.as_view()),
    path("appointments/<int:pk>/", views.AppointmentDetailView.as_view()),
    path("diagnoses/", views.DiagnosisListCreateView.as_view()),
    path("diagnoses/<int:pk>/", views.DiagnosisDetailView.as_view()),
    path("prescriptions/", views.PrescriptionListCreateView.as_view()),
    path("prescriptions/<int:pk>/", views.PrescriptionDetailView.as_view()),
    path("messages/", views.MessageListCreateView.as_view()),
    path("messages/<int:pk>/", views.MessageDetailView.as_view()),
]
