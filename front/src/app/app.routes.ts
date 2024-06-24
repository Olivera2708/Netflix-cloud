import { Routes } from '@angular/router';
import {ViewMovieComponent} from "./movie/view-movie/view-movie.component";
import {AddMovieComponent} from "./movie/add-movie/add-movie.component";
import {SearchMoviesComponent} from "./movie/search-movies/search-movies.component";
import { LoginComponent } from './authentication/login/login.component';
import { RegistrationComponent } from './authentication/registration/registration.component';

export const routes: Routes = [
  { path: "movie", component: ViewMovieComponent},
  { path: "add", component: AddMovieComponent},
  { path: "search", component: SearchMoviesComponent},
  { path: "", component: LoginComponent},
  { path: "registration", component: RegistrationComponent}
];
