# Architecture

## Overview

The Medical Web Application is built as two separate services inside one monorepo:

- **Frontend:** Angular SPA
- **Backend:** Django + Django REST Framework API

The frontend and backend communicate only through HTTP/JSON.

---

## High-Level Structure

```text
Angular Frontend  <----HTTP / JSON---->  Django REST API  <---->  SQLite
```

---

## Responsibilities

### Frontend
- login/logout UI
- routing and navigation
- forms with `[(ngModel)]`
- API calls with `HttpClient`
- rendering patient and medical data
- displaying validation and server errors

### Backend
- authentication with JWT
- profile-based permissions (doctor vs patient)
- request validation
- CRUD for medical records
- linking created records to the authenticated user's profile
- returning JSON responses

---

## Access Model

The API determines access via *profile models* attached to Django `User`:

- **Doctor access**: `request.user.doctor_profile` exists
- **Patient access**: `request.user.patient_profile` exists

There is no `role` field returned by the API. “Admin” is only relevant to Django admin (`/admin/`).

### Doctor capabilities (REST API)
- view all patients
- create/update/delete diagnoses
- create/update/delete prescriptions

### Patient capabilities (REST API)
- register for a patient account
- view self patient profile only
- view own diagnoses only
- view own prescriptions only

---

## Main Backend Apps

The backend is intentionally kept small: a single Django app called `api` contains models, serializers, views, permissions, and URL routing.

---

## Main Models

- `DoctorProfile` (1:1 with `User`)
- `PatientProfile` (1:1 with `User`)
- `Diagnosis` (doctor -> patient)
- `Prescription` (doctor -> patient, optionally linked to a `Diagnosis`)

### Main Relationships
- `DoctorProfile.user -> OneToOne(User)`
- `PatientProfile.user -> OneToOne(User)`
- `Diagnosis.patient -> ForeignKey(PatientProfile)`
- `Diagnosis.recorded_by -> ForeignKey(DoctorProfile)`
- `Prescription.patient -> ForeignKey(PatientProfile)`
- `Prescription.prescribed_by -> ForeignKey(DoctorProfile)`
- `Prescription.diagnosis -> ForeignKey(Diagnosis, nullable)`

---

## Authentication

JWT authentication is used.

Main endpoints:
- `POST /api/auth/register/`
- `POST /api/auth/login/`
- `POST /api/auth/logout/`
- `POST /api/auth/refresh/`

Frontend stores the access token and sends it in:
```http
Authorization: Bearer <token>
```

---

## Data Flow

1. User action in Angular
2. Angular service sends request to Django API
3. Django authenticates user and checks permissions
4. Serializer validates input
5. Database operation is performed
6. JSON response is returned
7. Angular updates the UI

---

## Frontend Routes

- `/login`
- `/dashboard`
- `/patients`
- `/patients/:id`
- `/my-records`

---

## Development Setup

- Angular dev server: `http://localhost:4200`
- Django dev server: `http://127.0.0.1:8000`
- API base URL: `http://127.0.0.1:8000/api/`

CORS must allow:
- `http://localhost:4200`

---

## Key Decisions

- separate frontend and backend services
- single monorepo for submission convenience
- JWT auth for SPA-friendly authentication
- “roles” implemented via `DoctorProfile` / `PatientProfile` relationships
- SQLite for development/demo
