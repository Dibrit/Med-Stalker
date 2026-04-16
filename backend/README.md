# Backend

This folder contains the backend service for the **Medical Web Application**.  
It is built with **Django** and **Django REST Framework** and exposes a REST API consumed by the Angular frontend.

The backend is responsible for:
- authentication and authorization
- role-based permissions
- medical data storage
- request validation
- business logic
- JSON API responses

This backend is intended for a semester project / student demo environment. The default development setup uses **SQLite**, but the structure is organized so that it can be migrated to PostgreSQL later if needed.

---

## 1. Technology Stack

- Python
- Django
- Django REST Framework
- Simple JWT
- django-cors-headers
- SQLite (development)
- Postman (API testing)
- Optional local tooling:
    - `uv`
    - Docker / Docker Compose

`uv` is a modern Python project manager that works with `pyproject.toml`, creates a project virtual environment, and supports commands such as `uv sync` and `uv run`. Docker Compose supports defining services with a `build` section and environment configuration through `.env` / `env_file`.

---

## 2. Backend Responsibilities

The backend handles:

- login and logout
- JWT token generation and validation
- current-user identity endpoint
- doctor vs patient authorization
- patient profile management
- diagnosis CRUD
- prescription CRUD
- recommendation creation and retrieval
- cross-origin access for Angular development
- data ownership rules using `request.user`

The backend is the source of truth for:
- who is allowed to perform an action
- which doctor created a record
- which patient owns a record
- what input data is valid

---

## 3. Project Structure

Recommended backend structure:

```text
backend/
├── README.md
├── pyproject.toml
├── uv.lock
├── .env.example
├── manage.py
├── config/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
└── apps/
    ├── accounts/
    │   ├── models.py
    │   ├── serializers.py
    │   ├── views.py
    │   ├── urls.py
    │   └── permissions.py
    ├── patients/
    │   ├── models.py
    │   ├── serializers.py
    │   ├── views.py
    │   └── urls.py
    ├── medical/
    │   ├── models.py
    │   ├── serializers.py
    │   ├── views.py
    │   ├── managers.py
    │   └── urls.py
    └── core/
        ├── permissions.py
        ├── constants.py
        └── utils.py