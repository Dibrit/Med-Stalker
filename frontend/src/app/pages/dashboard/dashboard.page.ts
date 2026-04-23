import { CommonModule } from '@angular/common';
import { ChangeDetectorRef, Component, inject } from '@angular/core';
import { RouterLink } from '@angular/router';
import { forkJoin, of } from 'rxjs';
import { DiagnosisService } from '../../core/diagnoses/diagnosis.service';
import { PatientService } from '../../core/patients/patient.service';
import { PrescriptionService } from '../../core/prescriptions/prescription.service';
import { SessionService } from '../../core/session/session.service';
import { ToastService } from '../../shared/toast/toast.service';

@Component({
  standalone: true,
  imports: [CommonModule, RouterLink],
  templateUrl: './dashboard.page.html',
  styleUrl: './dashboard.page.scss'
})
export class DashboardPage {
  private readonly patients = inject(PatientService);
  private readonly diagnoses = inject(DiagnosisService);
  private readonly prescriptions = inject(PrescriptionService);
  readonly session = inject(SessionService);
  private readonly toasts = inject(ToastService);
  private readonly cdr = inject(ChangeDetectorRef);

  loading = true;
  error: string | null = null;

  counts = { patients: 0, diagnoses: 0, prescriptions: 0 };

  ngOnInit() {
    this.loading = true;
    this.error = null;

    const snapshot = this.session.snapshot();
    const session$ = snapshot.mode === 'unknown' ? this.session.hydrate() : of(snapshot);

    forkJoin({
      session: session$,
      patients: this.patients.list(),
      diagnoses: this.diagnoses.list(),
      prescriptions: this.prescriptions.list()
    }).subscribe({
      next: ({ session, patients, diagnoses, prescriptions }) => {
        const scopedDiagnoses =
          session.mode === 'patient' && session.selfPatient
            ? diagnoses.filter((diagnosis) => diagnosis.patient?.id === session.selfPatient?.id)
            : diagnoses;

        const scopedPrescriptions =
          session.mode === 'patient' && session.selfPatient
            ? prescriptions.filter((prescription) => prescription.patient?.id === session.selfPatient?.id)
            : prescriptions;

        this.counts = {
          patients: session.mode === 'patient' && session.selfPatient ? 1 : patients.length,
          diagnoses: scopedDiagnoses.length,
          prescriptions: scopedPrescriptions.length
        };
        this.loading = false;
        this.cdr.detectChanges();
      },
      error: () => {
        this.error = 'Could not load dashboard data.';
        this.loading = false;
        this.toasts.error(this.error);
        this.cdr.detectChanges();
      }
    });
  }
}
