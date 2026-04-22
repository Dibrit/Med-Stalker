import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../../environments/environment';

@Injectable({ providedIn: 'root' })
export class PrescriptionService {

  private baseUrl = environment.apiUrl;

  constructor(private http: HttpClient) {}

  getPrescriptions(patientId?: number) {
    let url = `${this.baseUrl}/prescriptions/`;
    if (patientId) {
      url += `?patient=${patientId}`;
    }
    return this.http.get(url);
  }

  createPrescription(data: any) {
    return this.http.post(`${this.baseUrl}/prescriptions/`, data);
  }

  deletePrescription(id: number) {
    return this.http.delete(`${this.baseUrl}/prescriptions/${id}/`);
  }
}