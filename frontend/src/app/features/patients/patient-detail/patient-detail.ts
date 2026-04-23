import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { PatientService } from '../../../core/services/patient';

@Component({
  selector: 'app-patient-detail',
  standalone: true,
  templateUrl: './patient-detail.html'
})
export class PatientDetailComponent implements OnInit {

  patient: any;

  constructor(
    private route: ActivatedRoute,
    private service: PatientService
  ) {}

  ngOnInit() {
    const id = this.route.snapshot.params['id'];

    this.service.getPatient(id)
      .subscribe(res => {
        this.patient = res;
      });
  }
}