import {CanActivateFn, Router, UrlSegment} from '@angular/router';
import {AuthenticationService} from "../authentication.service";
import {inject} from "@angular/core";
import {AdminPaths} from "./adminpaths";
import {RegularUserPaths} from "./regularuserpaths";

export const authGuard: CanActivateFn = (route, state) => {
  const authenticationService: AuthenticationService = inject(AuthenticationService);
  const router: Router = inject(Router);
  const path: string = getFullPath(route.url);
  const userRole = authenticationService.getRole();
  if (userRole === 'RegularUser' && checkForPaths(path, RegularUserPaths)) {
    return true;
  } else if (userRole === 'Admin' && checkForPaths(path, AdminPaths)) {
    return true;
  }else if (userRole === '') {
    if (path === '' || path === 'registration/') return true
    router.navigate(['']);
    return false;
  } else {
    router.navigate(['/search']);
    return false;
  }
};

function getFullPath(urlSegments: UrlSegment[]): string {
  let path = '';
  for (const urlSegment of urlSegments) {
    path += urlSegment.path + '/';
  }
  return path;
}

function checkForPaths(accessedPath: string, paths: string[]): boolean {
  for (const path of paths) {
    if (accessedPath.includes(path)) return true;
  }
  return false;
}
