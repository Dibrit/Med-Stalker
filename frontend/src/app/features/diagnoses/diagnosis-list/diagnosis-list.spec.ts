import { ComponentFixture, TestBed } from '@angular/core/testing';

import { DiagnosisList } from './diagnosis-list';

describe('DiagnosisList', () => {
  let component: DiagnosisList;
  let fixture: ComponentFixture<DiagnosisList>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [DiagnosisList]
    })
    .compileComponents();

    fixture = TestBed.createComponent(DiagnosisList);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
