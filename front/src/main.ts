import { bootstrapApplication } from '@angular/platform-browser';
// import { appConfig } from './app/app.config';
import { AppComponent } from './app/app.component';
import {HTTP_INTERCEPTORS, provideHttpClient, withInterceptorsFromDi} from "@angular/common/http";
import { Test2Interceptor } from './app/authentication/interceptor/test2.interceptor';
import { provideRouter } from '@angular/router';
import { routes } from './app/app.routes';
import { provideAnimations } from '@angular/platform-browser/animations';

// bootstrapApplication(AppComponent, appConfig)
//   .catch((err) => console.error(err));

// bootstrapApplication(AppComponent, {providers: [provideHttpClient()]});

bootstrapApplication(AppComponent, {providers: [
  provideHttpClient(
    withInterceptorsFromDi(),
  ),
  {provide: HTTP_INTERCEPTORS, useClass: Test2Interceptor, multi: true},
  provideRouter(routes),
  provideAnimations()
]})
.catch((err) => console.error(err));