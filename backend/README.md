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

- **Python 3.13+** (see `pyproject.toml` for `requires-python`)
- **[uv](https://docs.astral.sh/uv/)** package manager (install per [uv installation](https://docs.astral.sh/uv/getting-started/installation/))

---

## Environment variables

Local development can use a **`backend/.env`** file (gitignored). On startup, `config/settings.py` loads it with **`python-dotenv`**. Values that are **already set in the process environment are not overwritten** by the file, so production or CI can inject secrets and they take precedence.

1. Copy the template: `cp .env.example .env`
2. Edit `.env` with your values (see comments in `.env.example`).

Supported keys include those referenced in `config/settings.py` (for example `DJANGO_SECRET_KEY`, `DJANGO_LOG_LEVEL`, `API_LOG_LEVEL`). For production, prefer your host’s native mechanism (**systemd** `Environment=`, **Docker** `env_file` / `-e`, **Kubernetes** `Secret` + env) instead of committing a `.env` file.

To load the same keys into an interactive shell (for non-Django tools), common options are **[direnv](https://direnv.net/)** with an `.envrc` that sources `.env`, or running one-off commands with `export VAR=value` as your platform documents.

---

## Run the backend (local development)

All commands below assume your shell’s **current directory is `backend/`** (from the repository root: `cd backend`).

### First time on a machine

1. **Optional — environment file** (recommended so you can tune logging and secrets without exporting variables manually):

   ```bash
   cp .env.example .env
   ```

   See [Environment variables](#environment-variables) for what goes in `.env`.

2. **Install dependencies** (creates or updates `.venv/` and installs locked versions from `uv.lock`):

   ```bash
   uv sync
   ```

3. **Apply migrations** (creates/updates the SQLite database):

   ```bash
   uv run python manage.py migrate
   ```

4. **Optional — Django admin** (browse `/admin/` after starting the server):

   ```bash
   uv run python manage.py createsuperuser
   ```

You do **not** need `uv init` or `uv add` when working from this repository; dependencies are already declared in `pyproject.toml` and pinned in `uv.lock`.

### Start the API

```bash
uv run python manage.py runserver 0.0.0.0:8000
```

- **Base URL:** `http://localhost:8000`
- **API:** routes live under the app’s URL config (for example `/api/…`; see `docs/endpoints.md` at the repo root for a concise list).

Stop the server with **Ctrl+C**.

### After pulling changes or editing dependencies

```bash
uv sync
uv run python manage.py migrate
```

### If you change models

```bash
uv run python manage.py makemigrations
uv run python manage.py migrate
```

### Run tests

```bash
uv run python manage.py test
```

### Shell with Django context

```bash
uv run python manage.py shell
```

### Production note

For production deployments, set a strong **`DJANGO_SECRET_KEY`** in the process environment instead of relying on the development default in `config/settings.py`.

### Activating the virtualenv (optional)

`uv run …` already uses the project’s `.venv`. If you prefer an activated shell:

```bash
source .venv/bin/activate   # Linux / macOS
python manage.py runserver 0.0.0.0:8000
```
