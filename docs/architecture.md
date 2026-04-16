# Technical Specification and Work Plan

## Medical Web Application

**Stack:** Django + Django REST Framework, Angular
**Repository style:** Monorepo with separate frontend and backend services

---

## 1. Project overview

### 1.1 System purpose

The system is a web application for basic doctor–patient interaction and medical record management. It is designed for a semester project, so the scope should be realistic: authentication, patient listing, diagnosis assignment, prescription/recommendation creation, and viewing medical history.

The application supports two main user groups:

* **Doctors** who manage patient-related medical data
* **Patients** who log in and view their own diagnoses, prescriptions, and recommendations

The system is not intended to replace a hospital information system. It is a controlled academic project focused on demonstrating full-stack web development, API design, authentication, CRUD, role-based access, and clean separation between frontend and backend.

### 1.2 Main business flows

The core flows should be:

1. User logs in and receives JWT tokens
2. Doctor opens patient list
3. Doctor selects a patient
4. Doctor creates or updates a diagnosis for that patient
5. Doctor creates a prescription/recommendation linked to a diagnosis or directly to a patient
6. Patient logs in and sees their own medical information
7. Doctor or patient logs out

### 1.3 Roles and permissions

| Role    | Main permissions                                                                                                                               |
| ------- | ---------------------------------------------------------------------------------------------------------------------------------------------- |
| Doctor  | View patients, create/update/delete diagnoses, create/update/delete prescriptions, view medical history, manage doctor-created medical records |
| Patient | View own profile, view own diagnoses, view own prescriptions/recommendations                                                                   |
| Admin   | Manage users through Django admin, optionally seed test data                                                                                   |

### 1.4 Assumptions

To keep the project implementable in one semester, the following assumptions are recommended:

* There are only two business roles: `doctor` and `patient`
* A user has one account and one role
* Doctors do not edit patient authentication data directly
* Patients can only view their own medical data, not other patients
* Diagnoses and prescriptions are textual and simple, without file uploads
* Appointment scheduling is out of scope unless time remains
* The project uses **JWT authentication with SimpleJWT**
* Logout is implemented by blacklisting the refresh token
* Initial user creation can be handled through Django admin or fixtures, not full public registration
* The first version should prioritize correctness and clean architecture over advanced UI

---

## 2. Architecture

### 2.1 Overall architecture

The system should follow a **client-server architecture** with a strict separation between frontend and backend:

* **Angular frontend** acts as a standalone SPA client
* **Django REST Framework backend** exposes a REST API
* Both live in one repository, but are developed and run as separate services

This approach satisfies the course requirement while reflecting real-world practice.

### 2.2 Interaction between Angular and Django

Angular communicates with Django exclusively through HTTP requests to REST endpoints.

**Typical flow:**

1. Angular login form sends credentials to `/api/auth/login/`
2. Django validates credentials and returns access + refresh tokens
3. Angular stores tokens
4. Angular includes `Authorization: Bearer <token>` in subsequent requests
5. Django verifies token and returns JSON responses
6. Angular renders data and handles errors in UI

### 2.3 Why this structure is appropriate

This structure is suitable because it:

* cleanly separates responsibilities
* allows backend and frontend students to work in parallel
* forces an explicit API contract early
* mirrors industry practice for SPA + API applications
* keeps deployment and local development manageable in a monorepo

### 2.4 Architectural decisions

Recommended decisions:

* **Monorepo** for simplified submission and shared documentation
* **Default Django User model** plus role/profile models to reduce complexity
* **DRF + SimpleJWT** for modern token-based auth
* **Angular services** as the only place for HTTP communication
* **Role-based backend checks** to prevent relying only on frontend restrictions
* **JSON-only communication** between frontend and backend

---

## 3. Backend technical specification

## 3.1 Backend apps/modules

Recommended Django apps:

| App               | Responsibility                                                         |
| ----------------- | ---------------------------------------------------------------------- |
| `accounts`        | authentication, roles, doctor/patient profiles, login/logout endpoints |
| `patients`        | patient profile data and patient-related access helpers                |
| `medical_records` | diagnoses, prescriptions, recommendations, medical history             |
| `common`          | shared utilities, permissions, mixins, constants                       |

A realistic structure is:

* `accounts`: user role handling, auth endpoints
* `patients`: patient profile model and patient-specific endpoints
* `medical_records`: diagnosis and prescription CRUD

## 3.2 Proposed data model

Use Django’s built-in `User` model for authentication and add profiles.

### Model 1: `DoctorProfile`

Represents doctor-specific information.

**Fields**

* `user` → `OneToOneField(User)`
* `specialization` → `CharField`
* `license_number` → `CharField`
* `created_at` → `DateTimeField`

### Model 2: `PatientProfile`

Represents patient-specific information.

**Fields**

* `user` → `OneToOneField(User)`
* `date_of_birth` → `DateField`
* `phone` → `CharField`
* `address` → `TextField`
* `emergency_contact` → `CharField`
* `created_at` → `DateTimeField`

### Model 3: `Diagnosis`

Represents a medical diagnosis assigned to a patient.

**Fields**

* `patient` → `ForeignKey(PatientProfile, on_delete=CASCADE, related_name='diagnoses')`
* `doctor` → `ForeignKey(DoctorProfile, on_delete=CASCADE, related_name='diagnoses')`
* `title` → `CharField`
* `description` → `TextField`
* `status` → `CharField` with choices such as `active`, `resolved`
* `created_by` → `ForeignKey(User, on_delete=SET_NULL, null=True, related_name='created_diagnoses')`
* `created_at` → `DateTimeField`
* `updated_at` → `DateTimeField`

### Model 4: `Prescription`

Represents a prescription or recommendation.

**Fields**

* `patient` → `ForeignKey(PatientProfile, on_delete=CASCADE, related_name='prescriptions')`
* `doctor` → `ForeignKey(DoctorProfile, on_delete=CASCADE, related_name='prescriptions')`
* `diagnosis` → `ForeignKey(Diagnosis, on_delete=SET_NULL, null=True, blank=True, related_name='prescriptions')`
* `medication_name` → `CharField`
* `dosage` → `CharField`
* `instructions` → `TextField`
* `start_date` → `DateField`
* `end_date` → `DateField`
* `created_by` → `ForeignKey(User, on_delete=SET_NULL, null=True, related_name='created_prescriptions')`
* `created_at` → `DateTimeField`

### Optional Model 5: `Recommendation`

If the course allows extra scope, this can store non-medication advice.
If time is limited, keep recommendations as text in `Prescription.instructions`.

## 3.3 Required ForeignKey relationships

This design includes more than the required minimum:

* `Diagnosis.patient` → `PatientProfile`
* `Diagnosis.doctor` → `DoctorProfile`
* `Prescription.patient` → `PatientProfile`
* `Prescription.doctor` → `DoctorProfile`
* `Prescription.diagnosis` → `Diagnosis`

## 3.4 Optional custom model manager

A custom manager makes sense for `Diagnosis`.

```python
class ActiveDiagnosisManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(status='active')
```

Use it to quickly query currently active diagnoses. This is optional but demonstrates good design.

## 3.5 Authentication approach

Use:

* `djangorestframework`
* `djangorestframework-simplejwt`
* `rest_framework_simplejwt.token_blacklist`

### Endpoints

* `POST /api/auth/login/`
* `POST /api/auth/logout/`
* `POST /api/auth/refresh/`
* `GET /api/auth/me/`

### Login

Request:

```json
{
  "username": "doctor1",
  "password": "secret123"
}
```

Response:

```json
{
  "access": "jwt-access-token",
  "refresh": "jwt-refresh-token",
  "user": {
    "id": 5,
    "username": "doctor1",
    "role": "doctor"
  }
}
```

### Logout

Frontend sends refresh token to logout endpoint. Backend blacklists it.

Request:

```json
{
  "refresh": "jwt-refresh-token"
}
```

Response:

```json
{
  "detail": "Logged out successfully."
}
```

## 3.6 Full CRUD support

The primary full CRUD model should be **Diagnosis**.

Why Diagnosis is a good CRUD target:

* central business object
* easy to demonstrate create/read/update/delete
* naturally linked to both patient and doctor
* visible in both backend and frontend flows

Prescription may also support CRUD, but Diagnosis must be fully implemented at minimum.

## 3.7 Linking created objects to authenticated user

Whenever a diagnosis or prescription is created, the backend must ignore any `created_by` value from the client and set it from `request.user`.

Example logic:

```python
serializer.save(created_by=request.user, doctor=request.user.doctorprofile)
```

This ensures:

* auditability
* data integrity
* no spoofing from frontend

## 3.8 Serializer strategy

### Serializers based on `serializers.Serializer`

Use these for request/response payloads that do not map directly to one model.

#### 1. `LoginSerializer`

For login request validation.

Fields:

* `username`
* `password`

#### 2. `LogoutSerializer`

For logout request validation.

Fields:

* `refresh`

Optional third:

* `UserSummarySerializer` for `/api/auth/me/` response if not using `ModelSerializer`

### Serializers based on `serializers.ModelSerializer`

#### 1. `DiagnosisSerializer`

Used for CRUD on diagnoses.

Include:

* patient id
* doctor id (read-only)
* title
* description
* status
* timestamps

#### 2. `PrescriptionSerializer`

Used for CRUD on prescriptions.

Include:

* patient id
* diagnosis id
* medication_name
* dosage
* instructions
* start_date
* end_date
* timestamps

Optional extras:

* `PatientProfileSerializer`
* nested lightweight serializers for detail pages

### Serializer design recommendation

Use:

* **write serializer** for create/update payloads
* **read serializer** for list/detail responses if you want richer output

Example:

* `DiagnosisWriteSerializer`
* `DiagnosisReadSerializer`

This is not mandatory, but it keeps payloads clean.

## 3.9 View strategy

### Function-Based Views with DRF decorators

At least 2 are required.

#### FBV 1: `login_view`

Use `@api_view(['POST'])`

* validates username/password
* issues JWT tokens
* returns token + user info

#### FBV 2: `logout_view`

Use `@api_view(['POST'])`

* validates refresh token
* blacklists token
* returns success message

Optional FBV 3:

* `current_user_view` with `GET`

### Class-Based Views using `APIView`

At least 2 are required.

#### CBV 1: `DiagnosisListCreateAPIView`

* `GET` list diagnoses
* `POST` create diagnosis

#### CBV 2: `DiagnosisDetailAPIView`

* `GET` retrieve diagnosis
* `PUT` update diagnosis
* `DELETE` remove diagnosis

Optional CBVs:

* `PatientListAPIView`
* `PatientDetailAPIView`
* `PrescriptionListCreateAPIView`

### Permissions

Recommended custom permissions:

* `IsDoctor`
* `IsPatient`
* `IsOwnerPatientOrDoctor`

Examples:

* only doctors can create diagnosis/prescription
* patients can only read their own records
* doctors can read all patient records or only those assigned in project scope

## 3.10 Filtering and query behavior

Useful backend behavior:

* `/api/patients/` returns all patients for doctor view
* `/api/diagnoses/?patient_id=3` filters diagnoses for a patient
* `/api/prescriptions/?patient_id=3` filters prescriptions for a patient
* `/api/my/diagnoses/` returns only logged-in patient’s diagnoses

This keeps the frontend simple.

## 3.11 CORS configuration

Install `django-cors-headers`.

Recommended config for Angular dev server:

```python
INSTALLED_APPS = [
    ...
    "corsheaders",
    "rest_framework",
    ...
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    ...
]

CORS_ALLOWED_ORIGINS = [
    "http://localhost:4200",
]

CORS_ALLOW_CREDENTIALS = True
```

## 3.12 Postman collection organization

Commit Postman assets into the repo under `docs/postman/`.

Recommended folders in the collection:

1. Auth

   * Login
   * Logout
   * Refresh token
   * Current user

2. Patients

   * List patients
   * Patient detail

3. Diagnoses

   * List diagnoses
   * Create diagnosis
   * Retrieve diagnosis
   * Update diagnosis
   * Delete diagnosis

4. Prescriptions

   * List prescriptions
   * Create prescription
   * Update prescription
   * Delete prescription

### Postman best practices

Include:

* environment variables:

  * `base_url`
  * `access_token`
  * `refresh_token`
  * `patient_id`
  * `diagnosis_id`

* one example request body per endpoint

* one saved example response per endpoint

* notes about required role and auth header

---

## 4. Frontend technical specification

## 4.1 Angular structure

The frontend should be built as a modular SPA with feature grouping.

### Recommended modules/folders

| Folder/Module             | Responsibility                                        |
| ------------------------- | ----------------------------------------------------- |
| `core/`                   | singleton services, auth service, interceptor, guards |
| `shared/`                 | reusable components, interfaces, utilities            |
| `features/auth/`          | login page, auth state                                |
| `features/patients/`      | patient list, patient detail                          |
| `features/diagnoses/`     | diagnosis list/form                                   |
| `features/prescriptions/` | prescription list/form                                |

A practical student-level structure is feature folders plus a `core` folder.

## 4.2 Proposed components

Recommended components:

* `login-page`
* `navbar`
* `dashboard-page`
* `patient-list-page`
* `patient-detail-page`
* `diagnosis-form`
* `diagnosis-list`
* `prescription-form`
* `prescription-list`
* `error-message`

## 4.3 Interfaces

Define TypeScript interfaces matching API payloads.

### `user.interface.ts`

```ts
export interface User {
  id: number;
  username: string;
  role: 'doctor' | 'patient';
}
```

### `patient.interface.ts`

```ts
export interface Patient {
  id: number;
  user_id: number;
  full_name: string;
  date_of_birth: string;
  phone: string;
  address: string;
}
```

### `diagnosis.interface.ts`

```ts
export interface Diagnosis {
  id: number;
  patient: number;
  doctor: number;
  title: string;
  description: string;
  status: 'active' | 'resolved';
  created_at: string;
  updated_at: string;
}
```

### `prescription.interface.ts`

```ts
export interface Prescription {
  id: number;
  patient: number;
  doctor: number;
  diagnosis: number | null;
  medication_name: string;
  dosage: string;
  instructions: string;
  start_date: string;
  end_date: string;
  created_at: string;
}
```

### `auth-response.interface.ts`

```ts
export interface AuthResponse {
  access: string;
  refresh: string;
  user: User;
}
```

## 4.4 API service design

Use Angular `HttpClient` services.
At minimum, one service must handle API communication, but in practice use multiple focused services.

Recommended services:

* `AuthService`
* `PatientService`
* `DiagnosisService`
* `PrescriptionService`

If the course demands only one service, a single `ApiService` can be used, but feature-based services are cleaner.

### Example responsibilities

| Service               | Methods                                                                         |
| --------------------- | ------------------------------------------------------------------------------- |
| `AuthService`         | `login()`, `logout()`, `getCurrentUser()`                                       |
| `PatientService`      | `getPatients()`, `getPatientById()`                                             |
| `DiagnosisService`    | `getDiagnoses()`, `createDiagnosis()`, `updateDiagnosis()`, `deleteDiagnosis()` |
| `PrescriptionService` | `getPrescriptions()`, `createPrescription()`                                    |

## 4.5 Routing

At least 3 named routes are required. Recommended routing:

| Route           | Component                    | Purpose                  |
| --------------- | ---------------------------- | ------------------------ |
| `/login`        | `LoginPageComponent`         | authentication           |
| `/dashboard`    | `DashboardPageComponent`     | landing page after login |
| `/patients`     | `PatientListPageComponent`   | doctor patient list      |
| `/patients/:id` | `PatientDetailPageComponent` | view one patient’s data  |
| `/my-records`   | `PatientOwnRecordsComponent` | patient self-view        |

Three minimum routes should definitely be:

* `/login`
* `/patients`
* `/patients/:id`

## 4.6 JWT authentication flow

The frontend auth flow should be:

1. User enters credentials on login page
2. `AuthService.login()` sends POST request
3. Tokens are stored in `localStorage`
4. HTTP interceptor adds bearer token to protected requests
5. Route guard blocks private pages if token is missing
6. Logout button calls backend logout, clears storage, redirects to `/login`

### HTTP interceptor responsibilities

* attach `Authorization` header
* optionally catch `401` responses
* redirect to login on invalid/expired token

## 4.7 Form structure using `[(ngModel)]`

Use template-driven forms with `FormsModule`, since the requirement explicitly mentions `[(ngModel)]`.

### Minimum controls to include

At least 4 controls should use `[(ngModel)]`, for example:

**Login form**

* username
* password

**Diagnosis form**

* title
* description
* status
* patient

**Prescription form**

* medication_name
* dosage
* instructions
* start_date

Example:

```html
<input [(ngModel)]="form.title" name="title" />
<textarea [(ngModel)]="form.description" name="description"></textarea>
<select [(ngModel)]="form.status" name="status"></select>
```

## 4.8 User actions/events that trigger API requests

At least 4 `(click)` events should trigger API calls. Recommended:

1. **Login button** → calls login API
2. **Load patients button** or page init action → calls patients list API
3. **Save diagnosis button** → calls diagnosis create/update API
4. **Delete diagnosis button** → calls diagnosis delete API
5. **Create prescription button** → calls prescription create API
6. **Logout button** → calls logout API

Example:

```html
<button (click)="login()">Login</button>
<button (click)="saveDiagnosis()">Save Diagnosis</button>
<button (click)="deleteDiagnosis(d.id)">Delete</button>
<button (click)="logout()">Logout</button>
```

## 4.9 Use of `@for` and `@if`

If using Angular’s newer syntax, use:

* `@for` for rendering lists
* `@if` for conditional UI states

Examples:

* render patient list
* render diagnoses list
* show loading state
* show error message
* show doctor-only buttons

If project setup or Angular version makes this difficult, `*ngFor` and `*ngIf` are acceptable fallback equivalents.

## 4.10 UI error handling

Every service call should handle errors and show user-facing messages.

Recommended behavior:

* show “Invalid username or password” on login failure
* show “Failed to load patients” on patient list error
* show validation errors under form fields when possible
* disable submit button while request is in progress
* use a reusable `error-message` component or simple alert block

Suggested structure in component:

```ts
errorMessage = '';
isLoading = false;
```

## 4.11 Basic CSS / UI guidance

Keep the UI simple but consistent.

Recommended rules:

* centered login form with card layout
* top navigation bar
* content container with max width
* tables or cards for patient/diagnosis lists
* form sections with labels and spacing
* button styles for primary, secondary, delete actions
* visible success/error messages
* avoid flashy design; prioritize readability

Suggested visual style:

* white cards on light gray background
* blue primary buttons
* red delete button
* consistent padding and border radius
* responsive layout with simple flex/grid

---

## 5. API design

## 5.1 REST API structure

Base prefix:

```text
/api/
```

Recommended endpoint groups:

* `/api/auth/`
* `/api/patients/`
* `/api/diagnoses/`
* `/api/prescriptions/`

## 5.2 Main endpoints

### Authentication endpoints

| Method | Endpoint             | Purpose                    | Request body             | Response body               |
| ------ | -------------------- | -------------------------- | ------------------------ | --------------------------- |
| POST   | `/api/auth/login/`   | authenticate and issue JWT | `{ username, password }` | `{ access, refresh, user }` |
| POST   | `/api/auth/logout/`  | blacklist refresh token    | `{ refresh }`            | `{ detail }`                |
| POST   | `/api/auth/refresh/` | refresh access token       | `{ refresh }`            | `{ access }`                |
| GET    | `/api/auth/me/`      | current logged-in user     | none                     | `{ id, username, role }`    |

### Patient endpoints

| Method | Endpoint              | Purpose        | Request body | Response body    |
| ------ | --------------------- | -------------- | ------------ | ---------------- |
| GET    | `/api/patients/`      | list patients  | none         | `[{...patient}]` |
| GET    | `/api/patients/{id}/` | patient detail | none         | `{...patient}`   |

### Diagnosis endpoints

| Method | Endpoint               | Purpose                                    | Request body                              | Response body      |
| ------ | ---------------------- | ------------------------------------------ | ----------------------------------------- | ------------------ |
| GET    | `/api/diagnoses/`      | list diagnoses, optional filter by patient | none or query param                       | `[{...diagnosis}]` |
| POST   | `/api/diagnoses/`      | create diagnosis                           | `{ patient, title, description, status }` | `{...diagnosis}`   |
| GET    | `/api/diagnoses/{id}/` | retrieve one diagnosis                     | none                                      | `{...diagnosis}`   |
| PUT    | `/api/diagnoses/{id}/` | update diagnosis                           | `{ patient, title, description, status }` | `{...diagnosis}`   |
| DELETE | `/api/diagnoses/{id}/` | delete diagnosis                           | none                                      | `204 No Content`   |

### Prescription endpoints

| Method | Endpoint                   | Purpose                   | Request body                                                                          | Response body         |
| ------ | -------------------------- | ------------------------- | ------------------------------------------------------------------------------------- | --------------------- |
| GET    | `/api/prescriptions/`      | list prescriptions        | none or query param                                                                   | `[{...prescription}]` |
| POST   | `/api/prescriptions/`      | create prescription       | `{ patient, diagnosis, medication_name, dosage, instructions, start_date, end_date }` | `{...prescription}`   |
| GET    | `/api/prescriptions/{id}/` | retrieve one prescription | none                                                                                  | `{...prescription}`   |
| PUT    | `/api/prescriptions/{id}/` | update prescription       | updated fields                                                                        | `{...prescription}`   |
| DELETE | `/api/prescriptions/{id}/` | delete prescription       | none                                                                                  | `204 No Content`      |

### Patient self-service endpoints

Optional but useful:

| Method | Endpoint                 | Purpose                                  |
| ------ | ------------------------ | ---------------------------------------- |
| GET    | `/api/my/diagnoses/`     | logged-in patient sees own diagnoses     |
| GET    | `/api/my/prescriptions/` | logged-in patient sees own prescriptions |

## 5.3 Endpoint-to-page mapping

| Frontend page/component      | Endpoints used                                                                                              |
| ---------------------------- | ----------------------------------------------------------------------------------------------------------- |
| `LoginPageComponent`         | `POST /api/auth/login/`                                                                                     |
| `NavbarComponent`            | `POST /api/auth/logout/`, `GET /api/auth/me/`                                                               |
| `PatientListPageComponent`   | `GET /api/patients/`                                                                                        |
| `PatientDetailPageComponent` | `GET /api/patients/{id}/`, `GET /api/diagnoses/?patient_id={id}`, `GET /api/prescriptions/?patient_id={id}` |
| `DiagnosisFormComponent`     | `POST /api/diagnoses/`, `PUT /api/diagnoses/{id}/`                                                          |
| `DiagnosisListComponent`     | `GET /api/diagnoses/`, `DELETE /api/diagnoses/{id}/`                                                        |
| `PrescriptionFormComponent`  | `POST /api/prescriptions/`, `PUT /api/prescriptions/{id}/`                                                  |
| `PatientOwnRecordsComponent` | `GET /api/my/diagnoses/`, `GET /api/my/prescriptions/`                                                      |

---

## 6. Repository structure

Recommended monorepo layout:

```text
medical-web-app/
│
├── backend/
│   ├── README.md
│   ├── requirements.txt
│   ├── manage.py
│   ├── .env.example
│   ├── config/
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── ...
│   ├── accounts/
│   ├── patients/
│   ├── medical_records/
│   ├── common/
│   └── tests/
│
├── frontend/
│   ├── README.md
│   ├── package.json
│   ├── angular.json
│   ├── .env.example
│   └── src/
│       ├── app/
│       │   ├── core/
│       │   ├── shared/
│       │   ├── features/
│       │   │   ├── auth/
│       │   │   ├── patients/
│       │   │   ├── diagnoses/
│       │   │   └── prescriptions/
│       │   ├── app.routes.ts
│       │   └── app.component.ts
│       └── styles.css
│
├── docs/
│   ├── architecture/
│   │   └── technical-spec.md
│   ├── api/
│   │   └── api-contract.md
│   ├── postman/
│   │   ├── MedicalWebApp.postman_collection.json
│   │   └── MedicalWebApp.local.postman_environment.json
│   └── notes/
│       └── team-decisions.md
│
├── .gitignore
└── README.md
```

### Placement guidance

* **documentation** → `docs/`
* **Postman collection** → `docs/postman/`
* **environment examples** → `backend/.env.example`, `frontend/.env.example`
* **shared notes and team decisions** → `docs/notes/team-decisions.md`

---

## 7. Work split for two people

## 7.1 Person 1 — Backend developer (Django)

Main responsibilities:

* Django project setup
* app structure creation
* models and migrations
* serializers
* auth endpoints with JWT
* diagnosis CRUD endpoints
* prescription endpoints
* permissions and role-based access
* CORS configuration
* seed data / admin setup
* Postman collection
* backend README

## 7.2 Person 2 — Frontend developer (Angular)

Main responsibilities:

* Angular project setup
* routing and page structure
* login page
* navbar and logout flow
* interfaces and services
* HTTP interceptor
* patient list and detail pages
* diagnosis and prescription forms
* error messages and loading states
* CSS styling
* frontend README

## 7.3 Tasks that can be done independently

| Backend-only                       | Frontend-only                                   |
| ---------------------------------- | ----------------------------------------------- |
| Create models and DB schema        | Create Angular layout and routing               |
| Implement authentication endpoints | Implement login form UI                         |
| Build serializers and API views    | Create interfaces and services                  |
| Configure permissions and CORS     | Build patient/diagnosis/prescription components |
| Create Postman collection          | Implement interceptor and error UI              |

## 7.4 Tasks requiring coordination

These must be agreed early:

| Shared contract          | Why it matters                                  |
| ------------------------ | ----------------------------------------------- |
| endpoint URLs            | frontend cannot call unstable paths             |
| auth response format     | needed for token storage                        |
| role field format        | needed for doctor/patient conditional rendering |
| diagnosis payload schema | needed for create/edit forms                    |
| error response shape     | needed for UI error display                     |
| filtering query params   | needed for patient detail page                  |

## 7.5 Early agreement checklist

Before coding too far, both students should agree on:

* API base URL
* endpoint names
* JSON field names
* which pages exist in version 1
* whether patient self-view endpoints are included
* exact auth storage strategy in frontend
* diagnosis status allowed values

---

## 8. Development plan

## 8.1 Phase 1 — Foundation

**Goal:** establish project skeleton and API contract

### Backend

* initialize Django project
* install DRF, SimpleJWT, corsheaders
* create apps
* configure settings
* define core models
* run migrations

### Frontend

* initialize Angular app
* create folder/module structure
* configure routing
* create placeholder pages
* create shared styles baseline

### Coordination

* finalize endpoint list
* finalize TypeScript interfaces based on sample API payloads
* commit initial monorepo structure

## 8.2 Phase 2 — Authentication

**Goal:** both sides can log in and access protected routes

### Backend

* implement login/logout/refresh/me endpoints
* configure JWT
* create doctor/patient seed users
* test in Postman

### Frontend

* build login page
* implement `AuthService`
* store JWT tokens
* add HTTP interceptor
* add logout flow
* protect routes

### Dependency

Frontend auth UI depends on backend auth response format.

## 8.3 Phase 3 — Core medical data

**Goal:** diagnosis CRUD working end to end

### Backend

* implement patient list/detail endpoints
* implement diagnosis list/create/detail/update/delete
* link created objects to `request.user`
* add permission checks

### Frontend

* implement patient list page
* implement patient detail page
* implement diagnosis list rendering
* implement diagnosis create/edit form
* connect buttons to API

### Dependency

Frontend diagnosis form depends on agreed diagnosis payload schema.

## 8.4 Phase 4 — Prescriptions

**Goal:** expand medical workflow

### Backend

* implement prescription endpoints
* optional filter by patient
* validate diagnosis linkage where relevant

### Frontend

* create prescription form
* create prescription list
* integrate into patient detail page

## 8.5 Phase 5 — Polish and stabilization

**Goal:** clean submission-ready version

### Backend

* improve validation
* finalize Postman collection
* add admin improvements
* basic tests if time allows

### Frontend

* improve loading and error handling
* add UI polish
* confirm role-based rendering
* cleanup unused components

### Shared

* verify end-to-end flows
* record screenshots if needed for course submission
* update documentation

## 8.6 Recommended order for parallel work

Best order so both students can progress simultaneously:

1. Agree on data model and endpoint contract
2. Backend builds auth first
3. Frontend builds login shell and routing in parallel
4. Backend builds patient + diagnosis APIs
5. Frontend builds patient pages using mocked data first
6. Connect diagnosis flows
7. Add prescriptions
8. Final integration and cleanup

This order reduces blocking.

---

## 9. Documentation plan

## 9.1 Root README

A short root `README.md` should include:

* project title and short description
* monorepo overview
* links to:

  * `backend/README.md`
  * `frontend/README.md`
  * `docs/architecture/technical-spec.md`
  * `docs/postman/`

## 9.2 `backend/README.md`

This file should contain:

1. backend purpose and scope
2. tech stack
3. setup instructions

   * create virtual environment
   * install requirements
   * configure `.env`
   * run migrations
   * create superuser
   * run server
4. installed packages
5. app/module structure
6. model summary
7. authentication flow
8. endpoint overview
9. sample test users
10. CORS settings note
11. Postman collection location

## 9.3 `frontend/README.md`

This file should contain:

1. frontend purpose and scope
2. Angular version and dependencies
3. install and run instructions
4. environment configuration
5. route structure
6. component structure
7. services and interceptor overview
8. auth storage strategy
9. styling approach
10. known limitations

## 9.4 Additional docs in `docs/`

Recommended files:

* `docs/architecture/technical-spec.md`
  full project specification

* `docs/api/api-contract.md`
  endpoint contract with sample payloads

* `docs/notes/team-decisions.md`
  any changes agreed during development

* `docs/postman/MedicalWebApp.postman_collection.json`
  required Postman export

---

## 10. Recommended implementation details

## 10.1 Minimal backend endpoint set for first working version

To keep scope realistic, the first complete version should include:

* auth login/logout/refresh/me
* patient list/detail
* diagnosis CRUD
* prescription create/list

That is enough to demonstrate:

* models
* relationships
* auth
* CRUD
* frontend integration
* role-based access

## 10.2 Suggested permission rules

Recommended rules:

* Doctor:

  * can list patients
  * can create diagnosis/prescription
  * can edit/delete own created diagnosis records
* Patient:

  * cannot create diagnosis/prescription
  * can view only their own records
* Admin:

  * unrestricted via admin panel

## 10.3 Suggested validation rules

Examples:

* `title` cannot be empty
* `end_date` must be after `start_date`
* only doctor users can create medical records
* patient id must exist
* diagnosis linked in prescription must belong to the same patient

---

## 11. Final blueprint summary

This project should be implemented as a **single monorepo containing two clearly separated services**:

* **Django + DRF backend** responsible for data, rules, authentication, and REST endpoints
* **Angular frontend** responsible for routing, UI, forms, token handling, and API consumption

The recommended core domain model is:

* `DoctorProfile`
* `PatientProfile`
* `Diagnosis`
* `Prescription`

This satisfies the backend model requirement and provides a clean, realistic medical workflow.

The recommended primary CRUD object is **Diagnosis**, supported by:

* `ModelSerializer` classes for domain models
* plain `Serializer` classes for auth payloads
* `@api_view` function-based auth endpoints
* `APIView` class-based CRUD endpoints

The frontend should implement:

* login/logout with JWT
* interceptor-based auth header injection
* patient list/detail routes
* diagnosis and prescription forms using `[(ngModel)]`
* conditional rendering with `@if` / `@for`
* basic but clean CSS and error messaging

The two students can work in parallel after agreeing on the API contract early. That contract is the most important coordination point in the project.

---

## 12. Immediate next tasks for each student

### Backend student — start here

1. Create Django project and apps
2. Configure DRF, SimpleJWT, corsheaders
3. Implement models and migrations
4. Implement login/logout/me endpoints
5. Implement diagnosis CRUD
6. Export first Postman collection

### Frontend student — start here

1. Create Angular project structure
2. Configure routes and basic pages
3. Implement login form and auth service
4. Add interceptor and logout
5. Build patient list/detail UI with mocked data first
6. Replace mocks with real API calls once backend endpoints stabilize
