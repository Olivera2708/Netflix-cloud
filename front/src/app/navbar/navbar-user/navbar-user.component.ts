import { Component } from '@angular/core';
import { MatAnchor } from '@angular/material/button';
import { MatToolbar } from '@angular/material/toolbar';
import { RouterLink } from '@angular/router';

@Component({
  selector: 'app-navbar-user',
  standalone: true,
  imports: [
    MatToolbar,
    RouterLink,
    MatAnchor,
  ],
  templateUrl: './navbar-user.component.html',
  styleUrl: './navbar-user.component.css'
})
export class NavbarUserComponent {

}
