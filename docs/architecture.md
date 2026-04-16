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
- role-based permissions
- request validation
- CRUD for medical records
- linking created records to `request.user`
- returning JSON responses

---

## User Roles

### Doctor
- view patients
- create/update/delete diagnoses
- create/update/delete prescriptions
- create recommendations

### Patient
- view only own profile and own medical records

### Admin
- manage users and data through Django admin

---

## Main Backend Apps

- `accounts` — user model and authentication
- `patients` — patient profiles
- `medical` — diagnoses, prescriptions, recommendations
- `core` — shared permissions and utilities

---

## Main Models

- `User`
- `PatientProfile`
- `Diagnosis`
- `Prescription`
- `Recommendation`

### Main Relationships
- `PatientProfile.user -> OneToOne(User)`
- `Diagnosis.patient -> ForeignKey(PatientProfile)`
- `Diagnosis.doctor -> ForeignKey(User)`
- `Prescription.patient -> ForeignKey(PatientProfile)`
- `Prescription.doctor -> ForeignKey(User)`
- `Prescription.diagnosis -> ForeignKey(Diagnosis)`
- `Recommendation.patient -> ForeignKey(PatientProfile)`
- `Recommendation.doctor -> ForeignKey(User)`

---

## Authentication

JWT authentication is used.

Main endpoints:
- `POST /api/auth/login/`
- `POST /api/auth/logout/`
- `GET /api/auth/me/`

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
- custom user model with role field
- SQLite for development/demo
