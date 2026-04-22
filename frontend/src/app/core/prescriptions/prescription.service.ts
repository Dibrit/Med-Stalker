import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { apiUrl } from '../api';
import { Prescription } from '../models';

export interface PrescriptionCreateRequest {
  patient_id: number;
  diagnosis?: number | null;
  medication_name?: string | null;
  instructions: string;
  issued_at: string; // ISO datetime
  valid_until?: string | null; // YYYY-MM-DD or null
}

export type PrescriptionUpdateRequest = Partial<PrescriptionCreateRequest>;

@Injectable({ providedIn: 'root' })
export class PrescriptionService {
  private readonly http = inject(HttpClient);

  list(): Observable<Prescription[]> {
    return this.http.get<Prescription[]>(apiUrl('prescriptions/'));
  }

  get(id: number): Observable<Prescription> {
    return this.http.get<Prescription>(apiUrl(`prescriptions/${id}/`));
  }

  create(req: PrescriptionCreateRequest): Observable<Prescription> {
    return this.http.post<Prescription>(apiUrl('prescriptions/'), req);
  }

  update(id: number, req: PrescriptionUpdateRequest): Observable<Prescription> {
    return this.http.patch<Prescription>(apiUrl(`prescriptions/${id}/`), req);
  }

  delete(id: number): Observable<void> {
    return this.http.delete<void>(apiUrl(`prescriptions/${id}/`));
  }
}

