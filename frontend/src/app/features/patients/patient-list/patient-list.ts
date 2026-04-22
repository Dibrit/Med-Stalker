import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { PatientService } from '../../../core/services/patient';
import { Router } from '@angular/router';

@Component({
  selector: 'app-patient-list',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './patient-list.html'
})
export class PatientListComponent implements OnInit {

  patients: any[] = [];
  loading = false;

  constructor(
    private patientService: PatientService,
    private router: Router
  ) {}

  ngOnInit() {
    this.loadPatients();
  }

  loadPatients() {
    this.loading = true;

    this.patientService.getPatients()
      .subscribe((res: any) => {
        this.patients = res;
        this.loading = false;
      });
  }

  openPatient(id: number) {
    this.router.navigate(['/patients', id]);
  }
}