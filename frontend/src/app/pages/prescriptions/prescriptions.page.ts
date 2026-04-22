import { CommonModule } from '@angular/common';
import { ChangeDetectorRef, Component, inject } from '@angular/core';
import { RouterLink } from '@angular/router';
import { forkJoin, of } from 'rxjs';
import { DiagnosisService } from '../../core/diagnoses/diagnosis.service';
import { Diagnosis, Prescription } from '../../core/models';
import { PrescriptionService } from '../../core/prescriptions/prescription.service';
import { SessionService, UserMode } from '../../core/session/session.service';
import { ToastService } from '../../shared/toast/toast.service';

@Component({
  standalone: true,
  imports: [CommonModule, RouterLink],
  templateUrl: './prescriptions.page.html',
  styleUrl: './prescriptions.page.scss'
})
export class PrescriptionsPage {
  private readonly diagnosesSvc = inject(DiagnosisService);
  private readonly prescriptionsSvc = inject(PrescriptionService);
  readonly session = inject(SessionService);
  private readonly toasts = inject(ToastService);
  private readonly cdr = inject(ChangeDetectorRef);

  loading = true;
  error: string | null = null;

  mode: UserMode = this.session.snapshot().mode;
  prescriptions: Prescription[] = [];
  private diagnosisTitles = new Map<number, string>();

  ngOnInit() {
    this.reload();
  }

  diagnosisLabel(id: number | null): string {
    if (id === null) return '—';
    return this.diagnosisTitles.get(id) ?? `Diagnosis #${id}`;
  }

  private reload() {
    this.loading = true;
    this.error = null;

    const snapshot = this.session.snapshot();
    const session$ = snapshot.mode === 'unknown' ? this.session.hydrate() : of(snapshot);

    forkJoin({
      session: session$,
      diagnoses: this.diagnosesSvc.list(),
      prescriptions: this.prescriptionsSvc.list()
    }).subscribe({
      next: ({ session, diagnoses, prescriptions }) => {
        this.mode = session.mode;

        const scopedDiagnoses = this.scopeDiagnoses(diagnoses, session.selfPatient?.id ?? null, session.mode);
        const scopedPrescriptions = this.scopePrescriptions(prescriptions, session.selfPatient?.id ?? null, session.mode);

        this.diagnosisTitles = new Map(scopedDiagnoses.map((diagnosis) => [diagnosis.id, diagnosis.title]));
        this.prescriptions = scopedPrescriptions
          .slice()
          .sort((left, right) => new Date(right.issued_at).getTime() - new Date(left.issued_at).getTime());

        this.loading = false;
        this.cdr.detectChanges();
      },
      error: () => {
        this.error = 'Could not load prescriptions.';
        this.loading = false;
        this.toasts.error(this.error);
        this.cdr.detectChanges();
      }
    });
  }

  private scopeDiagnoses(diagnoses: Diagnosis[], patientId: number | null, mode: UserMode) {
    if (mode !== 'patient' || patientId === null) return diagnoses;
    return diagnoses.filter((diagnosis) => diagnosis.patient?.id === patientId);
  }

  private scopePrescriptions(prescriptions: Prescription[], patientId: number | null, mode: UserMode) {
    if (mode !== 'patient' || patientId === null) return prescriptions;
    return prescriptions.filter((prescription) => prescription.patient?.id === patientId);
  }
}
