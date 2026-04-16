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
```

---

## Requirements

- Python 3.11+
- `uv`

---

## Build and Run

From the project root:

1. Move to backend folder:
   ```bash
   cd backend
   ```
2. Create virtual environment:
   ```bash
   uv venv
   ```
3. Activate environment:
   ```bash
   source .venv/bin/activate
   ```
4. Initialize project metadata (first run only):
   ```bash
   uv init --bare
   ```
5. Add dependencies:
   ```bash
   uv add django djangorestframework djangorestframework-simplejwt django-cors-headers
   ```
6. Sync environment:
   ```bash
   uv sync
   ```
7. Apply database migrations:
   ```bash
   uv run python manage.py makemigrations
   uv run python manage.py migrate
   ```
8. Create admin user (first run only):
   ```bash
   uv run python manage.py createsuperuser
   ```
9. Start backend service:
   ```bash
   uv run python manage.py runserver 0.0.0.0:8000
   ```

Backend base URL:
```text
http://localhost:8000
```
