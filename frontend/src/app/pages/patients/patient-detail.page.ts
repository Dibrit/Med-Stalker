import { CommonModule } from '@angular/common';
import { ChangeDetectorRef, Component, computed, inject } from '@angular/core';
import { FormsModule, NgForm } from '@angular/forms';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { forkJoin } from 'rxjs';
import { fieldErrors, summarizeError } from '../../core/api-errors';
import { Diagnosis, Patient, Prescription } from '../../core/models';
import { DiagnosisCreateRequest, DiagnosisService } from '../../core/diagnoses/diagnosis.service';
import { PrescriptionCreateRequest, PrescriptionService } from '../../core/prescriptions/prescription.service';
import { PatientService } from '../../core/patients/patient.service';
import { SessionService } from '../../core/session/session.service';
import { ToastService } from '../../shared/toast/toast.service';

type Tab = 'profile' | 'diagnoses' | 'prescriptions';

const DIAGNOSIS_STATUS_OPTIONS = [
  { value: 'active', label: 'Active' },
  { value: 'resolved', label: 'Resolved' },
  { value: 'chronic', label: 'Chronic' }
] as const;
type DiagnosisStatusValue = (typeof DIAGNOSIS_STATUS_OPTIONS)[number]['value'];

@Component({
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: './patient-detail.page.html',
  styleUrl: './patient-detail.page.scss'
})
export class PatientDetailPage {
  private readonly route = inject(ActivatedRoute);
  private readonly patientsSvc = inject(PatientService);
  private readonly diagnosesSvc = inject(DiagnosisService);
  private readonly prescriptionsSvc = inject(PrescriptionService);
  readonly session = inject(SessionService);
  private readonly toasts = inject(ToastService);
  private readonly cdr = inject(ChangeDetectorRef);

  tab: Tab = 'profile';

  loading = true;
  error: string | null = null;

  patientId = 0;
  patient: Patient | null = null;

  diagnoses: Diagnosis[] = [];
  prescriptions: Prescription[] = [];

  // Diagnoses form state
  diagSaving = false;
  diagEditingId: number | null = null;
  diagFieldErrors: Record<string, string[]> = {};
  diagNonFieldError: string | null = null;
  diagModel: {
    title: string;
    description: string;
    icd_code: string;
    status: DiagnosisStatusValue;
    diagnosed_at_local: string;
  } = { title: '', description: '', icd_code: '', status: 'active', diagnosed_at_local: '' };

  // Prescriptions form state
  rxSaving = false;
  rxEditingId: number | null = null;
  rxFieldErrors: Record<string, string[]> = {};
  rxNonFieldError: string | null = null;
  rxModel: {
    diagnosis: number | null;
    medication_name: string;
    instructions: string;
    issued_at_local: string;
    valid_until: string | null;
  } = { diagnosis: null, medication_name: '', instructions: '', issued_at_local: '', valid_until: null };

  readonly canEdit = computed(() => this.session.snapshot().mode === 'doctor');

  ngOnInit() {
    const id = Number(this.route.snapshot.paramMap.get('id'));
    this.patientId = Number.isFinite(id) ? id : 0;
    this.reload();
  }

  setTab(t: Tab) {
    this.tab = t;
  }

  private reload() {
    this.loading = true;
    this.error = null;
    forkJoin({
      patient: this.patientsSvc.get(this.patientId),
      diagnoses: this.diagnosesSvc.list(),
      prescriptions: this.prescriptionsSvc.list()
    }).subscribe({
      next: (res) => {
        this.patient = res.patient;
        this.diagnoses = res.diagnoses.filter((d) => d.patient?.id === this.patientId);
        this.prescriptions = res.prescriptions.filter((p) => p.patient?.id === this.patientId);
        this.loading = false;
        this.cdr.detectChanges();
      },
      error: () => {
        this.error = 'Patient not found or you do not have access.';
        this.loading = false;
        this.toasts.error(this.error);
        this.cdr.detectChanges();
      }
    });
  }

  // ---- Diagnoses ----
  startNewDiagnosis() {
    this.diagEditingId = null;
    this.diagFieldErrors = {};
    this.diagNonFieldError = null;
    this.diagModel = {
      title: '',
      description: '',
      icd_code: '',
      status: 'active',
      diagnosed_at_local: new Date().toISOString().slice(0, 16)
    };
  }

  editDiagnosis(d: Diagnosis) {
    const incomingStatus = (d.status ?? 'active').trim().toLowerCase() as DiagnosisStatusValue;
    const known = (DIAGNOSIS_STATUS_OPTIONS as readonly { value: string; label: string }[]).some((o) => o.value === incomingStatus);

    this.diagEditingId = d.id;
    this.diagFieldErrors = {};
    this.diagNonFieldError = null;
    this.diagModel = {
      title: d.title ?? '',
      description: (d.description ?? '') as string,
      icd_code: ((d.icd_code ?? '') as string).trim(),
      status: (known ? incomingStatus : 'active') as DiagnosisStatusValue,
      diagnosed_at_local: (d.diagnosed_at ? new Date(d.diagnosed_at).toISOString().slice(0, 16) : '')
    };
    this.tab = 'diagnoses';
  }

  cancelDiagnosisEdit() {
    this.diagEditingId = null;
    this.diagFieldErrors = {};
    this.diagNonFieldError = null;
  }

  submitDiagnosis(form: NgForm) {
    if (!this.canEdit()) return;

    this.diagNonFieldError = null;
    this.diagFieldErrors = {};
    if (form.invalid) return;

    const icd = this.diagModel.icd_code.trim();
    const status = this.diagModel.status;
    if (!icd) {
      this.diagFieldErrors = { icd_code: ['ICD code is required.'] };
      return;
    }
    if (!status) {
      this.diagFieldErrors = { status: ['Status is required.'] };
      return;
    }

    const dt = new Date(this.diagModel.diagnosed_at_local);
    if (Number.isNaN(dt.getTime())) {
      this.diagFieldErrors = { diagnosed_at: ['Invalid date.'] };
      return;
    }
    if (dt.getTime() > Date.now()) {
      this.diagFieldErrors = { diagnosed_at: ['Diagnosed time cannot be in the future.'] };
      return;
    }

    const req: DiagnosisCreateRequest = {
      patient_id: this.patientId,
      title: this.diagModel.title,
      description: this.diagModel.description || null,
      icd_code: icd,
      status,
      diagnosed_at: dt.toISOString()
    };

    this.diagSaving = true;
    const obs = this.diagEditingId
      ? this.diagnosesSvc.update(this.diagEditingId, req)
      : this.diagnosesSvc.create(req);

    obs.subscribe({
      next: () => {
        this.diagSaving = false;
        this.toasts.success(this.diagEditingId ? 'Diagnosis updated.' : 'Diagnosis created.');
        this.cancelDiagnosisEdit();
        this.reload();
        this.cdr.detectChanges();
      },
      error: (err) => {
        this.diagSaving = false;
        const payload = (err as any)?.error ?? {};
        this.diagNonFieldError = summarizeError(payload);
        this.diagFieldErrors = fieldErrors(payload);
        this.cdr.detectChanges();
      }
    });
  }

  deleteDiagnosis(d: Diagnosis) {
    if (!this.canEdit()) return;
    if (!confirm(`Delete diagnosis "${d.title}"?`)) return;
    this.diagnosesSvc.delete(d.id).subscribe({
      next: () => {
        this.toasts.success('Diagnosis deleted.');
        this.reload();
        this.cdr.detectChanges();
      },
      error: () => this.toasts.error('Could not delete diagnosis.')
    });
  }

  // ---- Prescriptions ----
  startNewRx() {
    this.rxEditingId = null;
    this.rxFieldErrors = {};
    this.rxNonFieldError = null;
    this.rxModel = {
      diagnosis: null,
      medication_name: '',
      instructions: '',
      issued_at_local: new Date().toISOString().slice(0, 16),
      valid_until: null
    };
  }

  editRx(p: Prescription) {
    this.rxEditingId = p.id;
    this.rxFieldErrors = {};
    this.rxNonFieldError = null;
    this.rxModel = {
      diagnosis: p.diagnosis ?? null,
      medication_name: (p.medication_name ?? '') as string,
      instructions: p.instructions ?? '',
      issued_at_local: (p.issued_at ? new Date(p.issued_at).toISOString().slice(0, 16) : ''),
      valid_until: p.valid_until ?? null
    };
    this.tab = 'prescriptions';
  }

  cancelRxEdit() {
    this.rxEditingId = null;
    this.rxFieldErrors = {};
    this.rxNonFieldError = null;
  }

  submitRx(form: NgForm) {
    if (!this.canEdit()) return;

    this.rxNonFieldError = null;
    this.rxFieldErrors = {};
    if (form.invalid) return;

    const issued = new Date(this.rxModel.issued_at_local);
    if (Number.isNaN(issued.getTime())) {
      this.rxFieldErrors = { issued_at: ['Invalid date.'] };
      return;
    }

    const req: PrescriptionCreateRequest = {
      patient_id: this.patientId,
      diagnosis: this.rxModel.diagnosis ?? null,
      medication_name: this.rxModel.medication_name || null,
      instructions: this.rxModel.instructions,
      issued_at: issued.toISOString(),
      valid_until: this.rxModel.valid_until ?? null
    };

    this.rxSaving = true;
    const obs = this.rxEditingId ? this.prescriptionsSvc.update(this.rxEditingId, req) : this.prescriptionsSvc.create(req);

    obs.subscribe({
      next: () => {
        this.rxSaving = false;
        this.toasts.success(this.rxEditingId ? 'Prescription updated.' : 'Prescription created.');
        this.cancelRxEdit();
        this.reload();
        this.cdr.detectChanges();
      },
      error: (err) => {
        this.rxSaving = false;
        const payload = (err as any)?.error ?? {};
        this.rxNonFieldError = summarizeError(payload);
        this.rxFieldErrors = fieldErrors(payload);
        this.cdr.detectChanges();
      }
    });
  }

  deleteRx(p: Prescription) {
    if (!this.canEdit()) return;
    if (!confirm('Delete prescription?')) return;
    this.prescriptionsSvc.delete(p.id).subscribe({
      next: () => {
        this.toasts.success('Prescription deleted.');
        this.reload();
        this.cdr.detectChanges();
      },
      error: () => this.toasts.error('Could not delete prescription.')
    });
  }
}

