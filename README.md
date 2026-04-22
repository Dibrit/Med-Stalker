# Med-Stalker
## Authors
Alexandr Chernov & Nesvetailov Artem

## Project Overview

This project is a **Medical Web Application** built for a Web Development course.

The main goal of the system is to create a web platform where **doctors** and **patients** can interact through a structured medical record system. Doctors can manage patient-related medical data, assign diagnoses, create prescriptions or recommendations, and manage appointments. Patients can log in, view their own medical information, and book appointments with doctors.

The project is designed as a full-stack application with:

- **Backend:** Django + Django REST Framework
- **Frontend:** Angular
- **Database:** SQLite

Both parts are stored in a **single monorepo**, but they are developed as **separate services** that communicate through a REST API.

---

## Main Purpose

The purpose of this project is to demonstrate how a modern web application can be built with:

- separate frontend and backend layers
- token-based authentication
- REST API communication
- CRUD operations
- role-based access
- structured project organization in a monorepo

This project is also intended to give two students a clear division of work:

- one student focuses on the **backend**
- one student focuses on the **frontend**

---

## Main Users

### Doctor
A doctor can:
- log in to the system
- view patients
- review and manage appointments assigned to them
- assign diagnoses
- create prescriptions or recommendations
- manage medical records

### Patient
A patient can:
- register for an account
- log in to the system
- browse doctors and request appointments
- view their own diagnoses
- view their own prescriptions and recommendations

---

## Core Features

- JWT-based patient registration, login, and logout
- doctor directory and appointment booking
- patient list and detail view
- diagnosis management
- prescription/recommendation management
- protected API endpoints
- frontend integration with backend API
- clean separation between services

---

## Repository Structure

```text
Med-Stalker/
├── backend/
├── frontend/
├── docs/
└── README.md
```
