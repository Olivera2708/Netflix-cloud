import { TestBed } from '@angular/core/testing';

import { Test2Interceptor } from './test2.interceptor';

describe('Test2Interceptor', () => {
  beforeEach(() => TestBed.configureTestingModule({
    providers: [
      Test2Interceptor
      ]
  }));

  it('should be created', () => {
    const interceptor: Test2Interceptor = TestBed.inject(Test2Interceptor);
    expect(interceptor).toBeTruthy();
  });
});
