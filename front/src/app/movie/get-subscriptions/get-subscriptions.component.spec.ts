import { ComponentFixture, TestBed } from '@angular/core/testing';

import { GetSubscriptionsComponent } from './get-subscriptions.component';

describe('GetSubscriptionsComponent', () => {
  let component: GetSubscriptionsComponent;
  let fixture: ComponentFixture<GetSubscriptionsComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [GetSubscriptionsComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(GetSubscriptionsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
