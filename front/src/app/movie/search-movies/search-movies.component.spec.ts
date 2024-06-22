import { ComponentFixture, TestBed } from '@angular/core/testing';

import { SearchMoviesComponent } from './search-movies.component';

describe('SearchMoviesComponent', () => {
  let component: SearchMoviesComponent;
  let fixture: ComponentFixture<SearchMoviesComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [SearchMoviesComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(SearchMoviesComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
