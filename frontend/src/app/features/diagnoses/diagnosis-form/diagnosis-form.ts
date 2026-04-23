import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { DiagnosisService } from '../../../core/services/diagnosis';
import { PatientService } from '../../../core/services/patient';

@Component({
  selector: 'app-diagnosis-form',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './diagnosis-form.html'
})
export class DiagnosisFormComponent {

  patients: any[] = [];

  data = {
    patient: null,
    title: '',
    description: '',
    status: 'active',
    diagnosed_at: ''
  };

  constructor(
    private service: DiagnosisService,
    private patientService: PatientService
  ) {}

  ngOnInit() {
    this.patientService.getPatients()
      .subscribe((res: any) => {
        this.patients = res;
      });
  }

  submit() {
    this.service.createDiagnosis(this.data)
      .subscribe(() => {
        alert('Diagnosis created');
      });
  }
}