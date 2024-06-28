import { Routes } from '@angular/router';
import { ViewMovieComponent } from "./movie/view-movie/view-movie.component";
import { AddMovieComponent } from "./movie/add-movie/add-movie.component";
import { SearchMoviesComponent } from "./movie/search-movies/search-movies.component";
import { LoginComponent } from './authentication/login/login.component';
import { RegistrationComponent } from './authentication/registration/registration.component';
import { authGuard } from './authentication/guard/auth.guard';
import {EditMovieComponent} from "./movie/edit-movie/edit-movie.component";
import {GetSubscriptionsComponent} from "./movie/get-subscriptions/get-subscriptions.component";
import {FeedMoviesComponent} from "./movie/feed-movies/feed-movies.component";

export const routes: Routes = [
  { path: "movie/:id", component: ViewMovieComponent, canActivate: [authGuard]},
  { path: "add", component: AddMovieComponent, canActivate: [authGuard]},
  { path: "search", component: SearchMoviesComponent, canActivate: [authGuard]},
  { path: "feed", component: FeedMoviesComponent, canActivate: [authGuard]},
  { path: "edit/:id", component: EditMovieComponent},
  { path: "", component: LoginComponent, canActivate: [authGuard]},
  { path: "registration", component: RegistrationComponent, canActivate: [authGuard]},
  { path: "subscriptions", component: GetSubscriptionsComponent, canActivate: [authGuard]}
];
