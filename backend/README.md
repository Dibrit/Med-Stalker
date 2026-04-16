# Backend
## Main goal

The backend must provide a REST API for the frontend and store all medical data.

The system should support:

- doctor and patient users
- login and logout with JWT
- patient data access
- diagnosis management
- prescription/recommendation management
- role-based access control

---

## What must be implemented

### 1. Models
Create at least **4 models**.

Recommended models:
- `DoctorProfile`
- `PatientProfile`
- `Diagnosis`
- `Prescription`

Requirements:
- include at least **2 ForeignKey** relationships
- optionally add **1 custom model manager**
- use SQLite as the database

---

### 2. Authentication
Implement **JWT-based authentication**.

Required endpoints:
- `POST /api/auth/login/`
- `POST /api/auth/logout/`
- `POST /api/auth/refresh/`

Behavior:
- login returns access and refresh tokens
- logout invalidates the refresh token
- protected endpoints require JWT in the `Authorization` header

---

### 3. API functionality
Implement REST endpoints for the main entities.

Minimum required functionality:
- list patients
- get patient details
- full CRUD for at least **one model**
- recommended CRUD target: `Diagnosis`
- create prescriptions/recommendations for patients

When creating medical records:
- link created objects to the authenticated user with `request.user`

---

### 4. Serializers
Required:
- at least **2 serializers** based on `serializers.Serializer`
- at least **2 serializers** based on `serializers.ModelSerializer`

Recommended:
- `LoginSerializer`
- `LogoutSerializer`
- `DiagnosisSerializer`
- `PrescriptionSerializer`

---

### 5. Views
Required:
- at least **2 Function-Based Views** using DRF decorators
- at least **2 Class-Based Views** using `APIView`

Recommended:
- function-based views for login and logout
- class-based views for diagnosis list/create and diagnosis detail/update/delete

---

### 6. CORS
Configure CORS using `django-cors-headers`.

Allow Angular dev server:
```text
http://localhost:4200