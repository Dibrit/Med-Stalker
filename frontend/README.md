# Frontend — Medical Web Application

This folder contains the frontend service for the Medical Web Application.  
It is built with **Angular** and communicates with the Django backend through a REST API.

## Stack

- Angular
- TypeScript
- HttpClient
- FormsModule
- CSS

## Responsibilities of the Frontend

The frontend is responsible for:

- login and logout flow
- route navigation
- calling backend APIs
- rendering patient and medical data
- form handling
- displaying validation and server errors
- basic styling and user experience

## Main User Flows

### Doctor
- log in
- view patient list
- open patient detail page
- create diagnosis
- update diagnosis
- delete diagnosis
- create prescription
- view recommendations

### Patient
- log in
- view own profile
- view own diagnoses
- view own prescriptions
- view own recommendations

## Recommended Angular Structure

```text
frontend/src/app/
├── core/
│   ├── services/
│   ├── interceptors/
│   ├── guards/
│   └── components/
├── shared/
│   ├── interfaces/
│   ├── components/
│   └── helpers/
└── features/
    ├── auth/
    ├── patients/
    ├── diagnoses/
    ├── prescriptions/
    └── recommendations/