import { Component } from '@angular/core';
import {MatToolbar} from "@angular/material/toolbar";
import {Router, RouterLink} from "@angular/router";
import {MatAnchor} from "@angular/material/button";
import { AuthenticationService } from '../../authentication/authentication.service';
import { NavbarAdminComponent } from '../navbar-admin/navbar-admin.component';
import { NavbarUserComponent } from '../navbar-user/navbar-user.component';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-navbar',
  standalone: true,
  imports: [
    MatToolbar,
    RouterLink,
    MatAnchor,
    NavbarAdminComponent,
    NavbarUserComponent,
    CommonModule
  ],
  templateUrl: './navbar.component.html',
  styleUrl: './navbar.component.css'
})
export class NavbarComponent {
  role: string = '';

  constructor(private router: Router, private authenticationService: AuthenticationService) {
    this.role = authenticationService.getRole();
  }

  logout() {
    this.authenticationService.signOut();
    this.router.navigate(['']);
  }
}
