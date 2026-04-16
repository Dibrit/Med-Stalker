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

Authorization header is required for protected endpoints.

---

## Roles

- `doctor`
- `patient`
- `admin`

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

### User
```json
{
  "id": 1,
  "username": "doctor",
  "first_name": "Alice",
  "last_name": "Smith",
  "role": "doctor"
}
```

### PatientProfile
```json
{
  "id": 3,
  "user": 7,
  "date_of_birth": "2000-05-12",
  "phone": "+77001234567",
  "address": "Almaty, Kazakhstan",
  "blood_type": "A+"
}
```

### Diagnosis
```json
{
  "id": 8,
  "patient": 3,
  "doctor": 1,
  "doctor_name": "Alice Smith",
  "disease_name": "Hypertension",
  "description": "Persistent elevated blood pressure",
  "status": "confirmed",
  "diagnosed_at": "2026-04-15"
}
```

### Prescription
```json
{
  "id": 5,
  "patient": 3,
  "doctor": 1,
  "diagnosis": 8,
  "medication_name": "Lisinopril",
  "dosage": "10 mg",
  "frequency": "Once daily",
  "instructions": "Take in the morning",
  "start_date": "2026-04-16",
  "end_date": "2026-05-16"
}
```

### Recommendation
```json
{
  "id": 4,
  "patient": 3,
  "doctor": 1,
  "title": "Lifestyle Advice",
  "content": "Reduce salt intake and exercise daily",
  "created_at": "2026-04-16T10:30:00Z"
}
```

---

## Authentication Endpoints

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
  "refresh": "jwt_refresh_token",
  "user": {
    "id": 1,
    "username": "doctor",
    "first_name": "Alice",
    "last_name": "Smith",
    "role": "doctor"
  }
}
```

### `POST /auth/logout/`
Request:
```json
{
  "refresh": "jwt_refresh_token"
}
```

Response:
```json
{
  "detail": "Logged out successfully"
}
```

### `GET /auth/me/`
Response:
```json
{
  "id": 1,
  "username": "doctor",
  "first_name": "Alice",
  "last_name": "Smith",
  "role": "doctor"
}
```

---

## Patient Endpoints

### `GET /patients/`
Purpose: list patients  
Access: doctor

Response:
```json
[
  {
    "id": 3,
    "user": 7,
    "date_of_birth": "2000-05-12",
    "phone": "+77001234567",
    "address": "Almaty, Kazakhstan",
    "blood_type": "A+"
  }
]
```

### `GET /patients/{id}/`
Purpose: patient detail  
Access: doctor, or patient if self

### `PUT /patients/{id}/`
### `PATCH /patients/{id}/`
Purpose: update patient profile  
Access: patient if self, optional for doctor

Request:
```json
{
  "phone": "+77005556677",
  "address": "Updated address"
}
```

---

## Diagnosis Endpoints

### `GET /diagnoses/`
Purpose: list diagnoses  
Access: doctor or patient (own only)

Optional query:
```http
GET /diagnoses/?patient=3
```

### `POST /diagnoses/`
Purpose: create diagnosis  
Access: doctor only

Request:
```json
{
  "patient": 3,
  "disease_name": "Hypertension",
  "description": "Persistent elevated blood pressure",
  "status": "confirmed",
  "diagnosed_at": "2026-04-15"
}
```

Response:
```json
{
  "id": 8,
  "patient": 3,
  "doctor": 1,
  "doctor_name": "Alice Smith",
  "disease_name": "Hypertension",
  "description": "Persistent elevated blood pressure",
  "status": "confirmed",
  "diagnosed_at": "2026-04-15"
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

> Backend must set `doctor = request.user` on create.

---

## Prescription Endpoints

### `GET /prescriptions/`
Purpose: list prescriptions

Optional query:
```http
GET /prescriptions/?patient=3
```

### `POST /prescriptions/`
Purpose: create prescription  
Access: doctor only

Request:
```json
{
  "patient": 3,
  "diagnosis": 8,
  "medication_name": "Lisinopril",
  "dosage": "10 mg",
  "frequency": "Once daily",
  "instructions": "Take in the morning",
  "start_date": "2026-04-16",
  "end_date": "2026-05-16"
}
```

Response:
```json
{
  "id": 5,
  "patient": 3,
  "doctor": 1,
  "diagnosis": 8,
  "medication_name": "Lisinopril",
  "dosage": "10 mg",
  "frequency": "Once daily",
  "instructions": "Take in the morning",
  "start_date": "2026-04-16",
  "end_date": "2026-05-16"
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

> Backend must set `doctor = request.user` on create.

---

## Recommendation Endpoints

### `GET /recommendations/`
Purpose: list recommendations

Optional query:
```http
GET /recommendations/?patient=3
```

### `POST /recommendations/`
Purpose: create recommendation  
Access: doctor only

Request:
```json
{
  "patient": 3,
  "title": "Lifestyle Advice",
  "content": "Reduce salt intake and exercise daily"
}
```

Response:
```json
{
  "id": 4,
  "patient": 3,
  "doctor": 1,
  "title": "Lifestyle Advice",
  "content": "Reduce salt intake and exercise daily",
  "created_at": "2026-04-16T10:30:00Z"
}
```

### `GET /recommendations/{id}/`
Purpose: recommendation detail

### `DELETE /recommendations/{id}/`
Purpose: delete recommendation  
Access: doctor only

---

## Frontend Mapping

- `LoginComponent` → `POST /auth/login/`
- `NavbarComponent` → `POST /auth/logout/`, `GET /auth/me/`
- `PatientListComponent` → `GET /patients/`
- `PatientDetailComponent` → `GET /patients/{id}/`
- `DiagnosisListComponent` → `GET /diagnoses/?patient={id}`
- `DiagnosisFormComponent` → `POST /diagnoses/`, `PATCH /diagnoses/{id}/`
- `PrescriptionListComponent` → `GET /prescriptions/?patient={id}`
- `PrescriptionFormComponent` → `POST /prescriptions/`, `PATCH /prescriptions/{id}/`

---

## Standard Error Examples

### Validation error
```json
{
  "disease_name": [
    "This field is required."
  ]
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
