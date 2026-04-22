import { CommonModule } from '@angular/common';
import { ChangeDetectorRef, Component, inject } from '@angular/core';
import { RouterLink } from '@angular/router';
import { forkJoin, of } from 'rxjs';
import { DiagnosisService } from '../../core/diagnoses/diagnosis.service';
import { Diagnosis } from '../../core/models';
import { SessionService, UserMode } from '../../core/session/session.service';
import { ToastService } from '../../shared/toast/toast.service';

@Component({
  standalone: true,
  imports: [CommonModule, RouterLink],
  templateUrl: './diagnoses.page.html',
  styleUrl: './diagnoses.page.scss'
})
export class DiagnosesPage {
  private readonly diagnosesSvc = inject(DiagnosisService);
  readonly session = inject(SessionService);
  private readonly toasts = inject(ToastService);
  private readonly cdr = inject(ChangeDetectorRef);

  loading = true;
  error: string | null = null;

  mode: UserMode = this.session.snapshot().mode;
  diagnoses: Diagnosis[] = [];

  ngOnInit() {
    this.reload();
  }

  private reload() {
    this.loading = true;
    this.error = null;

    const snapshot = this.session.snapshot();
    const session$ = snapshot.mode === 'unknown' ? this.session.hydrate() : of(snapshot);

    forkJoin({
      session: session$,
      diagnoses: this.diagnosesSvc.list()
    }).subscribe({
      next: ({ session, diagnoses }) => {
        this.mode = session.mode;

        const scopedDiagnoses =
          session.mode === 'patient' && session.selfPatient
            ? diagnoses.filter((diagnosis) => diagnosis.patient?.id === session.selfPatient?.id)
            : diagnoses;

        this.diagnoses = scopedDiagnoses
          .slice()
          .sort((left, right) => new Date(right.diagnosed_at).getTime() - new Date(left.diagnosed_at).getTime());

        this.loading = false;
        this.cdr.detectChanges();
      },
      error: () => {
        this.error = 'Could not load diagnoses.';
        this.loading = false;
        this.toasts.error(this.error);
        this.cdr.detectChanges();
      }
    });
  }
}
