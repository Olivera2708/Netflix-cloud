import {Injectable, inject} from '@angular/core';
import {HttpEvent, HttpEventType, HttpHandler, HttpInterceptor, HttpRequest,} from '@angular/common/http';
import {Observable, tap} from 'rxjs';
import {Router} from "@angular/router";
import {AuthenticationService} from "../authentication.service";

@Injectable()
export class Interceptor implements HttpInterceptor {
  constructor(private router: Router, private authService: AuthenticationService) { }

  intercept(req: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
    const accessToken: any = localStorage.getItem('accessToken');
    console.log(accessToken);
    if (accessToken) {
      const cloned = req.clone({
        headers: req.headers.set('Authorization', "Bearer " + accessToken),
      });
      return next.handle(cloned).pipe(tap({
        next: (event: HttpEvent<any>): void => {},
        error: (error): void => {
          if(error.status === 401) {
            this.authService.logout();
            this.authService.setUser();
            this.router.navigate(['']);
          }
        }
      }));
    } else {
      return next.handle(req);
    }
  }
}
