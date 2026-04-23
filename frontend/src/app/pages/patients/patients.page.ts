import { CommonModule } from '@angular/common';
import { ChangeDetectorRef, Component, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { Patient } from '../../core/models';
import { PatientService } from '../../core/patients/patient.service';
import { ToastService } from '../../shared/toast/toast.service';

@Component({
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: './patients.page.html',
  styleUrl: './patients.page.scss'
})
export class PatientsPage {
  private readonly patientsSvc = inject(PatientService);
  private readonly toasts = inject(ToastService);
  private readonly cdr = inject(ChangeDetectorRef);

  loading = true;
  error: string | null = null;
  query = '';
  patients: Patient[] = [];

  ngOnInit() {
    this.loading = true;
    this.error = null;
    this.patientsSvc.list().subscribe({
      next: (res) => {
        this.patients = res;
        this.loading = false;
        this.cdr.detectChanges();
      },
      error: () => {
        this.error = 'Could not load patients.';
        this.loading = false;
        this.toasts.error(this.error);
        this.cdr.detectChanges();
      }
    });
  }

  filtered(): Patient[] {
    const q = this.query.trim().toLowerCase();
    if (!q) return this.patients;
    return this.patients.filter((p) => {
      return (
        p.username.toLowerCase().includes(q) ||
        p.email.toLowerCase().includes(q) ||
        `${p.first_name} ${p.last_name}`.toLowerCase().includes(q) ||
        p.medical_record_number.toLowerCase().includes(q)
      );
    });
  }
}

