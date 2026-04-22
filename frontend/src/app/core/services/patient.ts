import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../../environments/environment';

@Injectable({ providedIn: 'root' })
export class PatientService {

  private baseUrl = environment.apiUrl;

  constructor(private http: HttpClient) {}

  getPatients() {
    return this.http.get(`${this.baseUrl}/patients/`);
  }

  getPatient(id: number) {
    return this.http.get(`${this.baseUrl}/patients/${id}/`);
  }
}