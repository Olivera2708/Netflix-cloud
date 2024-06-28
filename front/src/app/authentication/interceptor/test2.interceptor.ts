import { Injectable } from '@angular/core';
import {
  HttpRequest,
  HttpHandler,
  HttpEvent,
  HttpInterceptor
} from '@angular/common/http';
import { Observable, from } from 'rxjs';
import { tap, switchMap } from 'rxjs/operators';
import { Router } from '@angular/router';
import { AuthenticationService } from '../authentication.service';

@Injectable()
export class Test2Interceptor implements HttpInterceptor {
  constructor(private router: Router, private authService: AuthenticationService) { }

  intercept(req: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
    return from(this.authService.makeAuthenticatedRequest2()).pipe(
      switchMap((accessToken: string | null) => {
        if (accessToken) {
          const cloned = req.clone({
            headers: req.headers.set('Authorization', "Bearer " + accessToken)
          });
          return next.handle(cloned).pipe(
            tap({
              next: (event: HttpEvent<any>): void => {},
              error: (error): void => {
                if (error.status === 401) {
                  this.authService.logout();
                  this.authService.setUser();
                  this.router.navigate(['']);
                }
              }
            })
          );
        } else {
          return next.handle(req);
        }
      })
    );
  }
}
