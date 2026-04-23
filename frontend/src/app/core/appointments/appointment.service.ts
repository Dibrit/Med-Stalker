import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { apiUrl } from '../api';
import { Appointment, Doctor } from '../models';

export interface AppointmentCreateRequest {
  doctor_id: number;
  reason?: string | null;
  starts_at: string; // ISO datetime
  ends_at: string; // ISO datetime
}

export type AppointmentUpdateRequest = Partial<AppointmentCreateRequest> & { status?: string };

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

  delete(id: number): Observable<void> {
    return this.http.delete<void>(apiUrl(`appointments/${id}/`));
  }

  listDoctors(): Observable<Doctor[]> {
    return this.http.get<Doctor[]>(apiUrl('doctors/'));
  }

  getDoctorsBySpecialization(specialization: string): Observable<Doctor[]> {
    return this.http.get<Doctor[]>(apiUrl('doctors/'), {
      params: { specialization }
    });
  }
}
