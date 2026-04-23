import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../../environments/environment';

@Injectable({ providedIn: 'root' })
export class DiagnosisService {

  private baseUrl = environment.apiUrl;

  constructor(private http: HttpClient) {}

  getDiagnoses(patientId?: number) {
    let url = `${this.baseUrl}/diagnoses/`;
    if (patientId) {
      url += `?patient=${patientId}`;
    }
    return this.http.get(url);
  }

  createDiagnosis(data: any) {
    return this.http.post(`${this.baseUrl}/diagnoses/`, data);
  }

  deleteDiagnosis(id: number) {
    return this.http.delete(`${this.baseUrl}/diagnoses/${id}/`);
  }
}