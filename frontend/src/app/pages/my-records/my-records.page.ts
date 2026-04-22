import { CommonModule } from '@angular/common';
import { ChangeDetectorRef, Component, inject } from '@angular/core';
import { RouterLink } from '@angular/router';
import { forkJoin } from 'rxjs';
import { DiagnosisService } from '../../core/diagnoses/diagnosis.service';
import { Patient, Diagnosis, Prescription } from '../../core/models';
import { PatientService } from '../../core/patients/patient.service';
import { PrescriptionService } from '../../core/prescriptions/prescription.service';
import { SessionService } from '../../core/session/session.service';
import { ToastService } from '../../shared/toast/toast.service';

@Component({
  standalone: true,
  imports: [CommonModule, RouterLink],
  templateUrl: './my-records.page.html',
  styleUrl: './my-records.page.scss'
})
export class MyRecordsPage {
  private readonly patientsSvc = inject(PatientService);
  private readonly diagnosesSvc = inject(DiagnosisService);
  private readonly prescriptionsSvc = inject(PrescriptionService);
  readonly session = inject(SessionService);
  private readonly toasts = inject(ToastService);
  private readonly cdr = inject(ChangeDetectorRef);

  loading = true;
  error: string | null = null;

  me: Patient | null = null;
  diagnoses: Diagnosis[] = [];
  prescriptions: Prescription[] = [];

  ngOnInit() {
    this.loading = true;
    this.error = null;

    forkJoin({
      patients: this.patientsSvc.list(),
      diagnoses: this.diagnosesSvc.list(),
      prescriptions: this.prescriptionsSvc.list()
    }).subscribe({
      next: (res) => {
        const me = res.patients[0] ?? null;
        this.me = me;
        const id = me?.id;
        this.diagnoses = id ? res.diagnoses.filter((d) => d.patient?.id === id) : [];
        this.prescriptions = id ? res.prescriptions.filter((p) => p.patient?.id === id) : [];
        this.loading = false;
        this.cdr.detectChanges();
      },
      error: () => {
        this.error = 'Could not load your records.';
        this.loading = false;
        this.toasts.error(this.error);
        this.cdr.detectChanges();
      }
    });
  }
}
