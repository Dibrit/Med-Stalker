import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { apiUrl } from '../api';
import { Diagnosis } from '../models';

export interface DiagnosisCreateRequest {
  patient_id: number;
  title: string;
  description?: string | null;
  icd_code: string;
  status: string;
  diagnosed_at: string; // ISO datetime
}

export type DiagnosisUpdateRequest = Partial<DiagnosisCreateRequest>;

@Injectable({ providedIn: 'root' })
export class DiagnosisService {
  private readonly http = inject(HttpClient);

  list(): Observable<Diagnosis[]> {
    return this.http.get<Diagnosis[]>(apiUrl('diagnoses/'));
  }

  get(id: number): Observable<Diagnosis> {
    return this.http.get<Diagnosis>(apiUrl(`diagnoses/${id}/`));
  }

  create(req: DiagnosisCreateRequest): Observable<Diagnosis> {
    return this.http.post<Diagnosis>(apiUrl('diagnoses/'), req);
  }

  update(id: number, req: DiagnosisUpdateRequest): Observable<Diagnosis> {
    return this.http.patch<Diagnosis>(apiUrl(`diagnoses/${id}/`), req);
  }

  delete(id: number): Observable<void> {
    return this.http.delete<void>(apiUrl(`diagnoses/${id}/`));
  }
}

