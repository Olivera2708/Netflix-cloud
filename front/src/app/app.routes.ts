import { Routes } from '@angular/router';
import {ViewMovieComponent} from "./movie/view-movie/view-movie.component";
import {AddMovieComponent} from "./movie/add-movie/add-movie.component";
import {SearchMoviesComponent} from "./movie/search-movies/search-movies.component";
import {EditMovieComponent} from "./movie/edit-movie/edit-movie.component";

export const routes: Routes = [
  { path: "movie/:id", component: ViewMovieComponent},
  { path: "add", component: AddMovieComponent},
  { path: "edit/:id", component: EditMovieComponent},
  { path: "", component: SearchMoviesComponent}
];
