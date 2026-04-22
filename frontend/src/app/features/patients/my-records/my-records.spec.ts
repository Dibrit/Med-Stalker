import { ComponentFixture, TestBed } from '@angular/core/testing';

import { MyRecords } from './my-records';

describe('MyRecords', () => {
  let component: MyRecords;
  let fixture: ComponentFixture<MyRecords>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [MyRecords]
    })
    .compileComponents();

    fixture = TestBed.createComponent(MyRecords);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
