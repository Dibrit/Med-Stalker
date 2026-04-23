import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { apiUrl } from '../api';
import { Appointment, AppointmentStatus } from '../models';

export interface AppointmentCreateRequest {
  doctor_id: number;
  reason?: string | null;
  starts_at: string; // ISO datetime
  ends_at: string; // ISO datetime
}

export interface AppointmentUpdateRequest {
  status?: AppointmentStatus;
  reason?: string | null;
  starts_at?: string;
  ends_at?: string;
}

export interface AppointmentValidationResult {
  valid: boolean;
  errors: Partial<Record<'starts_at' | 'ends_at', string>>;
}

export function validateAppointmentWindow(
  startsAtInput: string | Date,
  endsAtInput: string | Date
): AppointmentValidationResult {
  const startsAt = startsAtInput instanceof Date ? startsAtInput : new Date(startsAtInput);
  const endsAt = endsAtInput instanceof Date ? endsAtInput : new Date(endsAtInput);
  const errors: Partial<Record<'starts_at' | 'ends_at', string>> = {};

  if (Number.isNaN(startsAt.getTime())) {
    errors.starts_at = 'Start time is invalid.';
  }
  if (Number.isNaN(endsAt.getTime())) {
    errors.ends_at = 'End time is invalid.';
  }
  if (errors.starts_at || errors.ends_at) {
    return { valid: false, errors };
  }

  if (endsAt <= startsAt) {
    errors.ends_at = 'End time must be after start time.';
  }

  if (startsAt.getDay() === 0 || startsAt.getDay() === 6) {
    errors.starts_at = 'Appointments can only be scheduled Monday through Friday.';
  }

  if (startsAt.toDateString() !== endsAt.toDateString()) {
    errors.ends_at = 'Appointment must start and end on the same workday.';
  }

  const startsMinutes = startsAt.getHours() * 60 + startsAt.getMinutes();
  const endsMinutes = endsAt.getHours() * 60 + endsAt.getMinutes();
  const businessStart = 8 * 60;
  const businessEnd = 18 * 60;

  if (startsMinutes < businessStart) {
    errors.starts_at = 'Appointment cannot start before 08:00.';
  }
  if (endsMinutes > businessEnd) {
    errors.ends_at = 'Appointment must end by 18:00.';
  }

  return { valid: Object.keys(errors).length === 0, errors };
}

@Injectable({ providedIn: 'root' })
export class AppointmentService {
  private readonly http = inject(HttpClient);

  list(): Observable<Appointment[]> {
    return this.http.get<Appointment[]>(apiUrl('appointments/'));
  }

  get(id: number): Observable<Appointment> {
    return this.http.get<Appointment>(apiUrl(`appointments/${id}/`));
  }

  create(req: AppointmentCreateRequest): Observable<Appointment> {
    return this.http.post<Appointment>(apiUrl('appointments/'), req);
  }

  update(id: number, req: AppointmentUpdateRequest): Observable<Appointment> {
    return this.http.patch<Appointment>(apiUrl(`appointments/${id}/`), req);
  }
}
