# Backend
## Main goal

The backend must provide a REST API for the frontend and store all medical data.

The system should support:

- doctor and patient users
- patient self-registration
- login and logout with JWT
- patient data access
- doctor directory access
- appointment booking and management
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
- `Appointment`
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
- `POST /api/auth/register/`
- `POST /api/auth/login/`
- `POST /api/auth/logout/`
- `POST /api/auth/refresh/`

Behavior:
- registration creates a regular Django `User` plus a `PatientProfile`
- only patients can self-register; doctors are created manually through Django admin
- login returns access and refresh tokens
- logout invalidates the refresh token
- protected endpoints require JWT in the `Authorization` header

---

### 3. API functionality
Implement REST endpoints for the main entities.

Minimum required functionality:
- list patients
- list doctors for patient booking
- get patient details
- full CRUD for at least **one model**
- recommended CRUD target: `Diagnosis`
- let patients create appointments by selecting a doctor
- create prescriptions/recommendations for patients

When creating medical records:
- link created objects to the authenticated user with `request.user`

Access model implemented in this repo:
- doctors and patients can list doctors
- doctors can list **all patients**
- doctors can list/retrieve/update appointments assigned to their own `DoctorProfile`
- doctors can only list/retrieve/update/delete diagnoses that were recorded by their own `DoctorProfile`
- doctors can only list/retrieve/update/delete prescriptions that were written by their own `DoctorProfile`
- patients can list/retrieve/update their own appointments and create new appointments
- patients can only view their own patient profile, diagnoses, and prescriptions

---

### 4. Serializers
Required:
- at least **2 serializers** based on `serializers.Serializer`
- at least **2 serializers** based on `serializers.ModelSerializer`

Recommended:
- `LoginSerializer`
- `LogoutSerializer`
- `DoctorSerializer`
- `AppointmentSerializer`
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

### Using the Makefile (recommended)

This folder includes a `Makefile` that wraps the common `uv run …` commands:

```bash
make help
```

Common targets:

```bash
make sync          # install/update dependencies into .venv (uses uv.lock)
make migrate       # apply migrations
make run           # start API on 0.0.0.0:8000
make test          # run tests with per-test pass/fail output
```

If you don’t have `make` installed, you can run the equivalent `uv …` commands shown below.

### First time on a machine

1. **Optional — environment file** (recommended so you can tune logging and secrets without exporting variables manually):

   ```bash
   cp .env.example .env
   ```

   See [Environment variables](#environment-variables) for what goes in `.env`.

2. **Install dependencies** (creates or updates `.venv/` and installs locked versions from `uv.lock`):

   ```bash
   uv sync   # or: make sync
   ```

3. **Apply migrations** (creates/updates the SQLite database):

   ```bash
   uv run python manage.py migrate   # or: make migrate
   ```

4. **Optional — Django admin** (browse `/admin/` after starting the server):

   ```bash
   uv run python manage.py createsuperuser   # or: make superuser
   ```

You do **not** need `uv init` or `uv add` when working from this repository; dependencies are already declared in `pyproject.toml` and pinned in `uv.lock`.

### Start the API

```bash
uv run python manage.py runserver 0.0.0.0:8000   # or: make run
```

- **Base URL:** `http://localhost:8000`
- **API:** routes live under the app’s URL config (for example `/api/…`; see `docs/endpoints.md` at the repo root for a concise list).

Stop the server with **Ctrl+C**.

### After pulling changes or editing dependencies

```bash
uv sync                         # or: make sync
uv run python manage.py migrate  # or: make migrate
```

### If you change models

```bash
uv run python manage.py makemigrations  # or: make makemigrations
uv run python manage.py migrate         # or: make migrate
```

### Run tests

```bash
uv run python manage.py test -v 2   # or: make test
```

`-v 2` tells Django to print each test name/description so you can see which tests passed before any failure stops the run.

### Seed realistic demo data (local dev)

This project includes a management command that generates **real-looking** demo users and medical records.

```bash
make seed
```

You can customize counts and keep the output reproducible:

```bash
uv run python manage.py seed_dev_data --seed 42 --doctors 5 --patients 30 --diagnoses 120 --prescriptions 120 --appointments 80
```

Created users are named like `demo_doctor_001` / `demo_patient_001` (override with `--prefix`) and all share the same dev password (override with `--password`).

### Shell with Django context

```bash
uv run python manage.py shell   # or: make shell
```

### Production note

For production deployments, set a strong **`DJANGO_SECRET_KEY`** in the process environment instead of relying on the development default in `config/settings.py`.

### Activating the virtualenv (optional)

`uv run …` already uses the project’s `.venv`. If you prefer an activated shell:

```bash
source .venv/bin/activate   # Linux / macOS
python manage.py runserver 0.0.0.0:8000
```
