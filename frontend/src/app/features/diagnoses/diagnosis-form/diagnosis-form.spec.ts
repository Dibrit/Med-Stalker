import { ComponentFixture, TestBed } from '@angular/core/testing';

import { DiagnosisForm } from './diagnosis-form';

describe('DiagnosisForm', () => {
  let component: DiagnosisForm;
  let fixture: ComponentFixture<DiagnosisForm>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [DiagnosisForm]
    })
    .compileComponents();

    fixture = TestBed.createComponent(DiagnosisForm);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
