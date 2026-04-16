# Med-Stalker
Alexandr Chernov
Nesvetailov Artem

A project built with **Django REST Framework** and **Angular**.

This project is a medical web application where doctors and patients interact through a web interface. Doctors can manage patient-related medical data, create diagnoses, issue prescriptions, and add recommendations. Patients can securely log in and view their own medical records.

## Project Structure

This repository is organized as a **monorepo** with two separate services:

- `backend/` — Django + Django REST Framework API
- `frontend/` — Angular single-page application

Even though both parts are stored in one repository, they are designed as separate services communicating through a REST API.

## Main Features

### Doctor
- Log in securely
- View patient list
- Open patient detail page
- Create, update, and delete diagnoses
- Create and manage prescriptions
- Add medical recommendations

### Patient
- Log in securely
- View personal medical records
- View diagnoses, prescriptions, and recommendations
- Access only own data

## Technology Stack

### Backend
- Python
- Django
- Django REST Framework
- Simple JWT
- django-cors-headers
- SQLite (development)

### Frontend
- Angular
- TypeScript
- HttpClient
- FormsModule
- CSS

## Architecture

The application follows a client-server architecture:

- Angular handles the user interface, routing, forms, and API calls.
- Django provides REST endpoints, authentication, permissions, and business logic.
- Authentication is implemented with JWT tokens.
- The frontend communicates with the backend using JSON over HTTP.

## Repository Layout

```text
medical-web-app/
├── README.md
├── docs/
│   ├── architecture.md
│   ├── api-contract.md
│   ├── work-plan.md
│   └── postman/
│       ├── medical-app.postman_collection.json
│       └── local.postman_environment.json
├── backend/
│   ├── README.md
│   ├── requirements.txt
│   ├── .env.example
│   ├── manage.py
│   ├── config/
│   └── apps/
│       ├── accounts/
│       ├── patients/
│       ├── medical/
│       └── core/
└── frontend/
    ├── README.md
    ├── package.json
    ├── angular.json
    └── src/
        ├── app/
        │   ├── core/
        │   ├── shared/
        │   └── features/
        ├── environments/
        └── styles.css