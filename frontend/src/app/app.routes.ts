import { Routes } from '@angular/router';
import { authGuard } from './core/auth/auth.guard';
import { doctorGuard } from './core/session/doctor.guard';

export const routes: Routes = [
  {
    path: '',
    pathMatch: 'full',
    redirectTo: 'dashboard'
  },
  {
    path: 'login',
    loadComponent: () => import('./pages/auth/login.page').then((m) => m.LoginPage)
  },
  {
    path: 'dashboard',
    canActivate: [authGuard],
    loadComponent: () => import('./pages/dashboard/dashboard.page').then((m) => m.DashboardPage)
  },
  {
    path: 'diagnoses',
    canActivate: [authGuard],
    loadComponent: () => import('./pages/diagnoses/diagnoses.page').then((m) => m.DiagnosesPage)
  },
  {
    path: 'prescriptions',
    canActivate: [authGuard],
    loadComponent: () => import('./pages/prescriptions/prescriptions.page').then((m) => m.PrescriptionsPage)
  },
  {
    path: 'patients',
    canActivate: [authGuard, doctorGuard],
    loadComponent: () => import('./pages/patients/patients.page').then((m) => m.PatientsPage)
  },
  {
    path: 'patients/:id',
    canActivate: [authGuard],
    loadComponent: () => import('./pages/patients/patient-detail.page').then((m) => m.PatientDetailPage)
  },
  {
    path: 'my-records',
    canActivate: [authGuard],
    loadComponent: () => import('./pages/my-records/my-records.page').then((m) => m.MyRecordsPage)
  },
  {
    path: '**',
    redirectTo: 'dashboard'
  }
];
