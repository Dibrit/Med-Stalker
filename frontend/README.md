# Frontend
## Main goal

The frontend must provide a clean user interface for doctors and patients and connect to the backend through REST APIs.

The application should support:

- login and logout
- navigation between pages
- viewing patients
- viewing diagnoses and prescriptions
- creating and updating diagnosis/prescription data
- handling API errors clearly

---

## What must be implemented

### 1. Routing
Create routing with at least **3 named routes**.

Recommended routes:
- `/login`
- `/patients`
- `/patients/:id`
- `/dashboard`

The user should be able to navigate between pages from the UI.

---

### 2. Authentication
Implement **JWT authentication flow**.

Required:
- login page
- logout functionality
- HTTP interceptor for attaching JWT token
- protected pages for authenticated users only

Behavior:
- login sends credentials to backend
- access token is stored on the client
- logout clears stored tokens and redirects to login

---

### 3. Services and API communication
Use Angular services with `HttpClient` for backend communication.

Required:
- at least **1 Angular service** for API calls

Recommended services:
- `AuthService`
- `PatientService`
- `DiagnosisService`
- `PrescriptionService`

The frontend should call backend endpoints for:
- login
- logout
- loading patients
- loading patient details
- creating/updating/deleting diagnoses
- creating/updating/deleting prescriptions

---

### 4. Interfaces
Create TypeScript interfaces for API data.

Recommended interfaces:
- `User`
- `Patient`
- `Diagnosis`
- `Prescription`
- `AuthResponse`

These interfaces should match backend JSON responses.

---

### 5. Forms
Use `FormsModule` and `[(ngModel)]`.

Required:
- at least **4 form controls** using `[(ngModel)]`

Recommended fields:
- username
- password
- diagnosis title
- diagnosis description
- medication name
- dosage

Possible forms:
- login form
- diagnosis form
- prescription form

---

### 6. User actions that trigger API requests
Implement at least **4 `(click)` events** that call the backend.

Recommended:
- login button
- save diagnosis button
- delete diagnosis button
- save prescription button
- logout button

---

### 7. Rendering data
Use:
- `@for` and `@if`

or, if needed:
- `*ngFor` and `*ngIf`

Use them for:
- patient list
- diagnosis list
- prescription list
- showing error messages
- showing loading or empty states

---

### 8. Error handling
API errors must be handled and shown in the UI.

Examples:
- invalid login credentials
- failed request to load patients
- failed save/update/delete actions

Recommended behavior:
- show message near the form or content area
- do not fail silently

---

### 9. Styling
Apply basic CSS so the app looks clean and usable.

Minimum expectations:
- styled login form
- readable lists or cards
- spaced form fields
- visible buttons
- clear error/success messages

The design can stay simple, but it should not look unfinished.

---

## Suggested pages/components

### Pages
- Login page
- Dashboard page
- Patient list page
- Patient detail page

### Components
- Navbar
- Diagnosis list
- Diagnosis form
- Prescription list
- Prescription form
- Error message block

---

## Requirements
- Node.js
- Angular CLI

---

## How to run

The Angular app now lives directly in the `frontend` folder (flat layout).

1. Go to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Run the development server:
   ```bash
   npx ng serve --port 4200
   ```
4. Open in browser:
   ```text
   http://localhost:4200
   ```
