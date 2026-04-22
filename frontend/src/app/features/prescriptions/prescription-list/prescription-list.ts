import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { PrescriptionService } from '../../../core/services/prescription';

@Component({
  selector: 'app-prescription-list',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './prescription-list.html'
})
export class PrescriptionListComponent implements OnInit {

  prescriptions: any[] = [];

  constructor(private service: PrescriptionService) {}

  ngOnInit() {
    this.load();
  }

  load() {
    this.service.getPrescriptions()
      .subscribe((res: any) => {
        this.prescriptions = res;
      });
  }

  delete(id: number) {
    this.service.deletePrescription(id)
      .subscribe(() => this.load());
  }
}