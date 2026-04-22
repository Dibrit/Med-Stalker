import { TestBed } from '@angular/core/testing';

import { Diagnosis } from './diagnosis';

describe('Diagnosis', () => {
  let service: Diagnosis;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(Diagnosis);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
