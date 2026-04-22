# API Contract

## Base URL

```text
http://127.0.0.1:8000/api/
```

## Headers

```http
Content-Type: application/json
Authorization: Bearer <access_token>
```

Authorization header is required for all endpoints except registration, login, and token refresh.

---

## Access Model

This backend does **not** expose a `role` field in the API. Access is determined by whether the authenticated `User` has:

- a `doctor_profile` (doctor access)
- a `patient_profile` (patient access)

`admin` access is only relevant for Django admin (`/admin/`), not the REST API.

---

## Common Response Codes

- `200 OK`
- `201 Created`
- `204 No Content`
- `400 Bad Request`
- `401 Unauthorized`
- `403 Forbidden`
- `404 Not Found`

---

## Data Shapes

### Patient
```json
{
  "id": 3,
  "username": "patient1",
  "email": "patient1@example.com",
  "first_name": "Pat",
  "last_name": "Ient",
  "date_of_birth": "2000-05-12",
  "phone": "+77001234567",
  "medical_record_number": "MRN-000123",
  "created_at": "2026-04-16T10:30:00Z",
  "updated_at": "2026-04-16T10:30:00Z"
}
```

### Diagnosis
```json
{
  "id": 8,
  "patient": {
    "id": 3,
    "username": "patient1",
    "email": "patient1@example.com",
    "first_name": "Pat",
    "last_name": "Ient",
    "date_of_birth": "2000-05-12",
    "phone": "+77001234567",
    "medical_record_number": "MRN-000123",
    "created_at": "2026-04-16T10:30:00Z",
    "updated_at": "2026-04-16T10:30:00Z"
  },
  "recorded_by_id": 1,
  "title": "Hypertension",
  "description": "Persistent elevated blood pressure",
  "icd_code": "I10",
  "status": "active",
  "diagnosed_at": "2026-04-15T09:00:00Z",
  "created_at": "2026-04-16T10:30:00Z",
  "updated_at": "2026-04-16T10:30:00Z"
}
```

### Prescription
```json
{
  "id": 5,
  "patient": {
    "id": 3,
    "username": "patient1",
    "email": "patient1@example.com",
    "first_name": "Pat",
    "last_name": "Ient",
    "date_of_birth": "2000-05-12",
    "phone": "+77001234567",
    "medical_record_number": "MRN-000123",
    "created_at": "2026-04-16T10:30:00Z",
    "updated_at": "2026-04-16T10:30:00Z"
  },
  "prescribed_by_id": 1,
  "diagnosis": 8,
  "medication_name": "Lisinopril",
  "instructions": "10 mg once daily, mornings",
  "issued_at": "2026-04-16T10:30:00Z",
  "valid_until": "2026-05-16",
  "created_at": "2026-04-16T10:30:00Z",
  "updated_at": "2026-04-16T10:30:00Z"
}
```

---

## Authentication Endpoints

### `POST /auth/register/`
Creates a patient account. This endpoint creates a `User` plus `PatientProfile`.
Doctors are not self-registered through the API and should be added via Django admin.

Request:
```json
{
  "username": "patient2",
  "email": "patient2@example.com",
  "first_name": "Pat",
  "last_name": "Ient",
  "password": "strong-password-123",
  "password_confirm": "strong-password-123",
  "date_of_birth": "2000-05-12",
  "phone": "+77001234567"
}
```

Response:
```json
{
  "patient": {
    "id": 3,
    "username": "patient2",
    "email": "patient2@example.com",
    "first_name": "Pat",
    "last_name": "Ient",
    "date_of_birth": "2000-05-12",
    "phone": "+77001234567",
    "medical_record_number": "MRN-AB12CD34",
    "created_at": "2026-04-16T10:30:00Z",
    "updated_at": "2026-04-16T10:30:00Z"
  },
  "access": "jwt_access_token",
  "refresh": "jwt_refresh_token"
}
```

### `POST /auth/login/`
Request:
```json
{
  "username": "doctor",
  "password": "doctor123"
}
```

Response:
```json
{
  "access": "jwt_access_token",
  "refresh": "jwt_refresh_token"
}
```

### `POST /auth/logout/`
Requires authentication.

Request:
```json
{
  "refresh": "jwt_refresh_token"
}
```

Response:
```json
{
  "detail": "Successfully logged out."
}
```

### `POST /auth/refresh/`
Purpose: exchange a refresh token for a new access token.

Request:
```json
{
  "refresh": "jwt_refresh_token"
}
```

Response:
```json
{
  "access": "new_jwt_access_token"
}
```

---

## Patient Endpoints

### `GET /patients/`
Purpose: list patients  
Access:

- doctor: sees **all** patients
- patient: sees **self** only

Response:
```json
[
  {
    "id": 3,
    "username": "patient1",
    "email": "patient1@example.com",
    "first_name": "Pat",
    "last_name": "Ient",
    "date_of_birth": "2000-05-12",
    "phone": "+77001234567",
    "medical_record_number": "MRN-000123",
    "created_at": "2026-04-16T10:30:00Z",
    "updated_at": "2026-04-16T10:30:00Z"
  }
]
```

### `GET /patients/{id}/`
Purpose: patient detail  
Access: doctor (any patient) or patient (self only)

---

## Diagnosis Endpoints

### `GET /diagnoses/`
Purpose: list diagnoses  
Access: doctor (all) or patient (own only)

### `POST /diagnoses/`
Purpose: create diagnosis  
Access: doctor only

Request:
```json
{
  "patient_id": 3,
  "title": "Hypertension",
  "description": "Persistent elevated blood pressure",
  "icd_code": "I10",
  "status": "active",
  "diagnosed_at": "2026-04-15T09:00:00Z"
}
```

Response:
```json
{
  "id": 8,
  "patient": {
    "id": 3,
    "username": "patient1",
    "email": "patient1@example.com",
    "first_name": "Pat",
    "last_name": "Ient",
    "date_of_birth": "2000-05-12",
    "phone": "+77001234567",
    "medical_record_number": "MRN-000123",
    "created_at": "2026-04-16T10:30:00Z",
    "updated_at": "2026-04-16T10:30:00Z"
  },
  "recorded_by_id": 1,
  "title": "Hypertension",
  "description": "Persistent elevated blood pressure",
  "icd_code": "I10",
  "status": "active",
  "diagnosed_at": "2026-04-15T09:00:00Z",
  "created_at": "2026-04-16T10:30:00Z",
  "updated_at": "2026-04-16T10:30:00Z"
}
```

### `GET /diagnoses/{id}/`
Purpose: diagnosis detail

### `PUT /diagnoses/{id}/`
### `PATCH /diagnoses/{id}/`
Purpose: update diagnosis  
Access: doctor only

Example request:
```json
{
  "status": "resolved"
}
```

### `DELETE /diagnoses/{id}/`
Purpose: delete diagnosis  
Access: doctor only

Response:
```http
204 No Content
```

Notes:

- `recorded_by_id` is set by the backend from the logged-in doctor's profile.
- `diagnosed_at` cannot be in the future.

---

## Prescription Endpoints

### `GET /prescriptions/`
Purpose: list prescriptions

Access: doctor (all) or patient (own only)

### `POST /prescriptions/`
Purpose: create prescription  
Access: doctor only

Request:
```json
{
  "patient_id": 3,
  "diagnosis": 8,
  "medication_name": "Lisinopril",
  "instructions": "10 mg once daily, mornings",
  "issued_at": "2026-04-16T10:30:00Z",
  "valid_until": "2026-05-16"
}
```

Response:
```json
{
  "id": 5,
  "patient": {
    "id": 3,
    "username": "patient1",
    "email": "patient1@example.com",
    "first_name": "Pat",
    "last_name": "Ient",
    "date_of_birth": "2000-05-12",
    "phone": "+77001234567",
    "medical_record_number": "MRN-000123",
    "created_at": "2026-04-16T10:30:00Z",
    "updated_at": "2026-04-16T10:30:00Z"
  },
  "prescribed_by_id": 1,
  "diagnosis": 8,
  "medication_name": "Lisinopril",
  "instructions": "10 mg once daily, mornings",
  "issued_at": "2026-04-16T10:30:00Z",
  "valid_until": "2026-05-16",
  "created_at": "2026-04-16T10:30:00Z",
  "updated_at": "2026-04-16T10:30:00Z"
}
```

### `GET /prescriptions/{id}/`
Purpose: prescription detail

### `PUT /prescriptions/{id}/`
### `PATCH /prescriptions/{id}/`
Purpose: update prescription  
Access: doctor only

### `DELETE /prescriptions/{id}/`
Purpose: delete prescription  
Access: doctor only

Response:
```http
204 No Content
```

Notes:

- `prescribed_by_id` is set by the backend from the logged-in doctor's profile.
- `diagnosis` is optional and may be `null`.

---

## Frontend Mapping

- `LoginComponent` → `POST /auth/login/`, `POST /auth/refresh/`
- `NavbarComponent` → `POST /auth/logout/`
- `PatientListComponent` → `GET /patients/`
- `PatientDetailComponent` → `GET /patients/{id}/`
- `DiagnosisListComponent` → `GET /diagnoses/`
- `DiagnosisFormComponent` → `POST /diagnoses/`, `PATCH /diagnoses/{id}/`
- `PrescriptionListComponent` → `GET /prescriptions/`
- `PrescriptionFormComponent` → `POST /prescriptions/`, `PATCH /prescriptions/{id}/`

---

## Standard Error Examples

### Validation error
```json
{
  "title": ["This field is required."]
}
```

### Unauthorized
```json
{
  "detail": "Authentication credentials were not provided."
}
```

### Forbidden
```json
{
  "detail": "You do not have permission to perform this action."
}
```

### Not found
```json
{
  "detail": "Not found."
}
```
