import { ComponentFixture, TestBed } from '@angular/core/testing';

import { EditMovieComponent } from './edit-movie.component';

describe('AddMovieComponent', () => {
  let component: EditMovieComponent;
  let fixture: ComponentFixture<EditMovieComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [EditMovieComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(EditMovieComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
