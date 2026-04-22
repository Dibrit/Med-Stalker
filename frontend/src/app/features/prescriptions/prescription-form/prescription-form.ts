import { Component, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { PrescriptionService } from '../../../core/services/prescription';
import { PatientService } from '../../../core/services/patient';
import { DiagnosisService } from '../../../core/services/diagnosis';

@Component({
  selector: 'app-prescription-form',
  standalone: true,
  imports: [FormsModule],
  templateUrl: './prescription-form.html'
})
export class PrescriptionFormComponent implements OnInit {

  patients: any[] = [];
  diagnoses: any[] = [];

  data = {
    patient: null,
    diagnosis: null,
    medication_name: '',
    instructions: '',
    issued_at: '',
    valid_until: ''
  };

  constructor(
    private service: PrescriptionService,
    private patientService: PatientService,
    private diagnosisService: DiagnosisService
  ) {}

  ngOnInit() {
    this.patientService.getPatients()
      .subscribe((res: any) => this.patients = res);

    this.diagnosisService.getDiagnoses()
      .subscribe((res: any) => this.diagnoses = res);
  }

  submit() {
    this.service.createPrescription(this.data)
      .subscribe(() => {
        alert('Prescription created');
      });
  }
}