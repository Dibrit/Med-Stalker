import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { apiUrl } from '../api';
import { Patient } from '../models';

@Injectable({ providedIn: 'root' })
export class PatientService {
  private readonly http = inject(HttpClient);

  list(): Observable<Patient[]> {
    return this.http.get<Patient[]>(apiUrl('patients/'));
  }

  get(id: number): Observable<Patient> {
    return this.http.get<Patient>(apiUrl(`patients/${id}/`));
  }
}

