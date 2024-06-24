import { Component } from '@angular/core';
import { NavigationEnd, Router, RouterOutlet } from '@angular/router';
import {NavbarComponent} from "./navbar/navbar/navbar.component";
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet, NavbarComponent, CommonModule],
  templateUrl: './app.component.html',
  styleUrl: './app.component.css'
})
export class AppComponent {
  title = 'Moviefy';
  showNavbar = true;

  constructor(private router: Router) {
    this.router.events.subscribe((event) => {
      if (event instanceof NavigationEnd) {
        this.updateNavbarVisibility(event.urlAfterRedirects);
      }
    });
  }

  updateNavbarVisibility(url: string) {
    const noNavbarRoutes = ['/registration', '/'];
    console.log(url)
    this.showNavbar = !noNavbarRoutes.includes(url);
  }
}
