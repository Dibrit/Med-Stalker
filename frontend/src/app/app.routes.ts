import { Routes } from '@angular/router';

import { LoginComponent } from './features/auth/login/login';
import { PatientListComponent } from './features/patients/patient-list/patient-list';
import { PatientDetailComponent } from './features/patients/patient-detail/patient-detail';

import { DiagnosisListComponent } from './features/diagnoses/diagnosis-list/diagnosis-list';
import { DiagnosisFormComponent } from './features/diagnoses/diagnosis-form/diagnosis-form';

import { PrescriptionListComponent } from './features/prescriptions/prescription-list/prescription-list';
import { PrescriptionFormComponent } from './features/prescriptions/prescription-form/prescription-form';
import { MyRecordsComponent } from './features/patients/my-records/my-records';

import { authGuard } from './core/guards/auth-guard';
import { roleGuard } from './core/guards/role-guard';

export const routes: Routes = [

  {path: 'login',component: LoginComponent},
  {path: 'patients',component: PatientListComponent,canActivate: [authGuard, roleGuard('doctor')]},
  {path: 'patients/:id',component: PatientDetailComponent,canActivate: [authGuard, roleGuard('doctor')]},
   {path: 'diagnoses',component: DiagnosisListComponent,canActivate: [authGuard, roleGuard('doctor')]},
   {path: 'diagnoses/new',component: DiagnosisFormComponent,canActivate: [authGuard, roleGuard('doctor')]},
  {path: 'prescriptions',component: PrescriptionListComponent,canActivate: [authGuard, roleGuard('doctor')]},
  {path: 'prescriptions/new',component: PrescriptionFormComponent,canActivate: [authGuard, roleGuard('doctor')]},
  {
  path: 'my-records',
  component: MyRecordsComponent,
  canActivate: [authGuard, roleGuard('patient')]
}
];