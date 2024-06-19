import { Routes } from '@angular/router';
import {ViewMovieComponent} from "./movie/view-movie/view-movie.component";
import {AddMovieComponent} from "./movie/add-movie/add-movie.component";

export const routes: Routes = [
  { path: "movie", component: ViewMovieComponent},
  { path: "add", component: AddMovieComponent}
];
