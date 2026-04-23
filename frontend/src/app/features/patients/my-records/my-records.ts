import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../../../environments/environment';

@Component({
  selector: 'app-my-records',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './my-records.html'
})
export class MyRecordsComponent implements OnInit {

  patient: any;
  diagnoses: any[] = [];
  prescriptions: any[] = [];

  loading = true;

  private api = environment.apiUrl;

  constructor(private http: HttpClient) {}

  ngOnInit() {
    this.loadData();
  }

  loadData() {
    const user = JSON.parse(localStorage.getItem('user') || 'null');
    this.http.get<any>(`${this.api}/patients/`)
      .subscribe(res => {
        this.patient = res.find((p: any) =>
          p.username === user?.username
        );

        if (!this.patient) {
          this.loading = false;
          return;
        }

        this.http.get<any[]>(`${this.api}/diagnoses/`)
          .subscribe(d => {
            this.diagnoses = d.filter(x => x.patient.id === this.patient.id);
          });
        this.http.get<any[]>(`${this.api}/prescriptions/`)
          .subscribe(p => {
            this.prescriptions = p.filter(x => x.patient.id === this.patient.id);
          });

        this.loading = false;
      });
  }
}