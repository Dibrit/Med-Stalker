import { CommonModule } from '@angular/common';
import { ChangeDetectorRef, Component, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { forkJoin } from 'rxjs';
import { AppointmentService } from '../../core/appointments/appointment.service';
import { Appointment, Doctor } from '../../core/models';
import { SessionService } from '../../core/session/session.service';
import { ToastService } from '../../shared/toast/toast.service';

@Component({
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: './book-appointment.page.html',
  styleUrl: './book-appointment.page.scss'
})
export class BookAppointmentPage {
  private readonly appointmentSvc = inject(AppointmentService);
  readonly session = inject(SessionService);
  private readonly toasts = inject(ToastService);
  private readonly cdr = inject(ChangeDetectorRef);

  loading = true;
  submitting = false;
  error: string | null = null;

  allDoctors: Doctor[] = [];
  filteredDoctors: Doctor[] = [];
  specializations: string[] = [];
  appointments: Appointment[] = [];

  selectedSpecialization: string = '';
  selectedDoctor: Doctor | null = null;
  appointmentReason: string = '';
  appointmentDate: string = '';
  appointmentTime: string = '';

  ngOnInit() {
    this.loadDoctors();
  }

  private loadDoctors() {
    this.loading = true;
    this.error = null;

    forkJoin({
      doctors: this.appointmentSvc.listDoctors(),
      appointments: this.appointmentSvc.list()
    }).subscribe({
      next: ({ doctors, appointments }) => {
        this.allDoctors = doctors;
        this.appointments = appointments.sort((a, b) =>
          new Date(b.starts_at).getTime() - new Date(a.starts_at).getTime()
        );

        const specializationSet = new Set<string>();
        doctors.forEach((doctor) => {
          if (doctor.specialization && doctor.specialization.trim()) {
            specializationSet.add(doctor.specialization);
          }
        });

        this.specializations = Array.from(specializationSet).sort();
        this.loading = false;
        this.cdr.detectChanges();
      },
      error: () => {
        this.error = 'Could not load doctors and appointments.';
        this.loading = false;
        this.toasts.error(this.error);
        this.cdr.detectChanges();
      }
    });
  }

  onSpecializationChange() {
    if (this.selectedSpecialization) {
      this.filteredDoctors = this.allDoctors
        .filter((doctor) => doctor.specialization === this.selectedSpecialization)
        .sort((a, b) => a.full_name.localeCompare(b.full_name));
    } else {
      this.filteredDoctors = [];
    }
    this.selectedDoctor = null;
  }

  bookAppointment() {
    if (!this.selectedDoctor) {
      this.toasts.error('Please select a doctor.');
      return;
    }

    if (!this.appointmentDate || !this.appointmentTime) {
      this.toasts.error('Please select a date and time.');
      return;
    }

    const appointmentDateTime = `${this.appointmentDate}T${this.appointmentTime}:00`;
    const endDateTime = new Date(new Date(appointmentDateTime).getTime() + 30 * 60000).toISOString();

    this.submitting = true;
    const patientId = this.session.snapshot().selfPatient?.id;

    if (!patientId) {
      this.toasts.error('Patient information not available.');
      this.submitting = false;
      return;
    }

    this.appointmentSvc.create({
      doctor_id: this.selectedDoctor.id,
      reason: this.appointmentReason || undefined,
      starts_at: new Date(appointmentDateTime).toISOString(),
      ends_at: endDateTime
    }).subscribe({
      next: (appointment) => {
        this.submitting = false;
        this.toasts.success('Appointment booked successfully!');
        this.resetForm();
        this.cdr.detectChanges();
      },
      error: (err) => {
        this.submitting = false;
        const errorMsg = err?.error?.detail || 'Could not book appointment.';
        this.toasts.error(errorMsg);
        this.cdr.detectChanges();
      }
    });
  }

  private resetForm() {
    this.selectedSpecialization = '';
    this.filteredDoctors = [];
    this.selectedDoctor = null;
    this.appointmentReason = '';
    this.appointmentDate = '';
    this.appointmentTime = '';
  }

  getDoctorDisplay(doctor: Doctor): string {
    return `${doctor.full_name} - ${doctor.specialization}`;
  }

  getAppointmentsForSelectedDoctor(): Appointment[] {
    if (!this.selectedDoctor) return [];
    return this.appointments.filter((appointment) => appointment.doctor.id === this.selectedDoctor?.id);
  }

  getMyAppointments(): Appointment[] {
    const snapshot = this.session.snapshot();
    if (snapshot.mode === 'patient' && snapshot.selfPatient) {
      return this.appointments.filter((appointment) => appointment.patient.id === snapshot.selfPatient!.id);
    }
    if (snapshot.mode === 'doctor') {
      return this.appointments;
    }
    return this.appointments;
  }

  compareDoctors(a: Doctor | null, b: Doctor | null): boolean {
    return a?.id === b?.id;
  }
}
