# API Endpoints Reference

This document consolidates endpoint expectations from:

- Root [`README.md`](/home/alexander/Projects/Med-Stalker/README.md)
- Backend [`backend/README.md`](/home/alexander/Projects/Med-Stalker/backend/README.md)
- Frontend [`frontend/README.md`](/home/alexander/Projects/Med-Stalker/frontend/README.md)

## Base URL

- Development (suggested): `http://localhost:8000`
- API prefix: `/api/`

## Authentication

JWT is required for protected endpoints via:

```http
Authorization: Bearer <access_token>
```

## Required Endpoints

These are explicitly required by `backend/README.md`.

| Method | Path | Auth Required | Purpose |
|---|---|---|---|
| POST | `/api/auth/login/` | No | Authenticate user and return tokens |
| POST | `/api/auth/logout/` | Yes | Invalidate refresh token (logout) |
| POST | `/api/auth/refresh/` | No (refresh token in body) | Issue a new access token |

### `POST /api/auth/login/`

- Description: User login with credentials.
- Request body (example):

```json
{
  "username": "doctor1",
  "password": "secret"
}
```

- Success response (example):

```json
{
  "access": "<jwt_access_token>",
  "refresh": "<jwt_refresh_token>"
}
```

### `POST /api/auth/logout/`

- Description: Logout by invalidating the refresh token.
- Requires valid access token.
- Request body (example):

```json
{
  "refresh": "<jwt_refresh_token>"
}
```

- Success response (example):

```json
{
  "detail": "Successfully logged out."
}
```

### `POST /api/auth/refresh/`

- Description: Obtain a new access token from a refresh token.
- Request body (example):

```json
{
  "refresh": "<jwt_refresh_token>"
}
```

- Success response (example):

```json
{
  "access": "<new_jwt_access_token>"
}
```

## Entity Endpoints (Required Functionality, Path Names Suggested)

The READMEs require this functionality, but do not strictly fix URL paths for these resources.
Paths below are recommended conventions for implementation and frontend integration.

### Patients

| Method | Path | Auth Required | Purpose |
|---|---|---|---|
| GET | `/api/patients/` | Yes | List patients |
| GET | `/api/patients/{id}/` | Yes | Get patient details |

### Diagnoses (full CRUD required for at least one model, `Diagnosis` is recommended)

| Method | Path | Auth Required | Purpose |
|---|---|---|---|
| GET | `/api/diagnoses/` | Yes | List diagnoses |
| POST | `/api/diagnoses/` | Yes | Create diagnosis |
| GET | `/api/diagnoses/{id}/` | Yes | Get diagnosis details |
| PUT | `/api/diagnoses/{id}/` | Yes | Replace diagnosis |
| PATCH | `/api/diagnoses/{id}/` | Yes | Partially update diagnosis |
| DELETE | `/api/diagnoses/{id}/` | Yes | Delete diagnosis |

### Prescriptions / Recommendations

The READMEs require create/manage functionality. Suggested endpoints:

| Method | Path | Auth Required | Purpose |
|---|---|---|---|
| GET | `/api/prescriptions/` | Yes | List prescriptions/recommendations |
| POST | `/api/prescriptions/` | Yes | Create prescription/recommendation |
| GET | `/api/prescriptions/{id}/` | Yes | Get prescription/recommendation details |
| PUT | `/api/prescriptions/{id}/` | Yes | Replace prescription/recommendation |
| PATCH | `/api/prescriptions/{id}/` | Yes | Partially update prescription/recommendation |
| DELETE | `/api/prescriptions/{id}/` | Yes | Delete prescription/recommendation |

## Common Error Responses (Suggested)

| Status | Meaning |
|---|---|
| 400 | Validation error (bad input) |
| 401 | Unauthorized (missing/invalid token) |
| 403 | Forbidden (role/access denied) |
| 404 | Resource not found |

## Notes for Frontend Integration

From `frontend/README.md`, the frontend should call endpoints for:

- login
- logout
- load patient list
- load patient detail
- create/update/delete diagnoses
- create/update/delete prescriptions

This reference aligns those expected calls with concrete REST-style paths.
