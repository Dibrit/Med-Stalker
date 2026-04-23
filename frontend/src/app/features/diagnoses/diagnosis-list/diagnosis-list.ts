import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { DiagnosisService } from '../../../core/services/diagnosis';

@Component({
  selector: 'app-diagnosis-list',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './diagnosis-list.html'
})
export class DiagnosisListComponent implements OnInit {

  diagnoses: any[] = [];

  constructor(private service: DiagnosisService) {}

  ngOnInit() {
    this.load();
  }

  load() {
    this.service.getDiagnoses()
      .subscribe((res: any) => {
        this.diagnoses = res;
      });
  }

  delete(id: number) {
    this.service.deleteDiagnosis(id)
      .subscribe(() => this.load());
  }
}