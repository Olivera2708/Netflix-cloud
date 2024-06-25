import { Component } from '@angular/core';
import {FormsModule} from "@angular/forms";
import {MatError, MatFormField, MatLabel} from "@angular/material/form-field";
import {MatIcon} from "@angular/material/icon";
import {MatIconButton} from "@angular/material/button";
import {MatInput} from "@angular/material/input";
import {MatLine} from "@angular/material/core";
import {MatList, MatListItem} from "@angular/material/list";
import {NgForOf, NgIf} from "@angular/common";
import {MovieService} from "../movie.service";
import {MatSnackBar} from "@angular/material/snack-bar";
import { CardModule } from 'primeng/card';
import {Router} from "@angular/router";
@Component({
  selector: 'app-search-movies',
  standalone: true,
  imports: [
    FormsModule,
    MatError,
    MatFormField,
    MatIcon,
    MatIconButton,
    MatInput,
    MatLabel,
    MatLine,
    MatList,
    MatListItem,
    NgForOf,
    NgIf,
    CardModule
  ],
  templateUrl: './search-movies.component.html',
  styleUrl: './search-movies.component.css'
})
export class SearchMoviesComponent {
  actors: string[] = [];
  newActor: string = '';
  genres: string[] = [];
  newGenre: string = '';
  directors: string[] = [];
  newDirector: string = '';
  title: string = '';
  description: string = '';
  errors: string = '';
  movies: any;

  constructor(private router: Router, private movieService: MovieService, private _snackBar: MatSnackBar) { }

  ngOnInit(): void {
    this.search();
  }
  addActor() {
    if (this.newActor.trim()) {
      this.actors.push(this.newActor.trim());
      this.newActor = '';
    }
  }

  removeActor(index: number) {
    this.actors.splice(index, 1);
  }

  addGenre() {
    if (this.newGenre.trim()) {
      this.genres.push(this.newGenre.trim());
      this.newGenre = '';
    }
  }

  removeGenre(index: number) {
    this.genres.splice(index, 1);
  }

  addDirector() {
    if (this.newDirector.trim()) {
      this.directors.push(this.newDirector.trim());
      this.newDirector = '';
    }
  }

  removeDirector(index: number) {
    this.directors.splice(index, 1);
  }



  search() {

    try {

      const payload = {
        metadata: {
          title: this.title,
          description: this.description,
          actors: this.actors,
          directors: this.directors,
          genres: this.genres,
        }
      }

      this.resetFields();

      this.movieService.searchMovie(payload.metadata.actors,
      payload.metadata.directors,
      payload.metadata.genres,
      payload.metadata.title,
      payload.metadata.description)
      .subscribe({
        next: (data) => {

          this.movies = data
        }
      })
    } catch (error) {
      console.error('Error converting file to base64:', error);
    }


  }

  private resetFields() {
    this.actors = [];
    this.newActor = '';
    this.genres = [];
    this.newGenre = '';
    this.directors = [];
    this.newDirector = '';
    this.title = '';
    this.description = '';
    this.errors = '';
  }


  onCardClick(id: string) {
    this.router.navigate(['/movie', id]);
  }

  editMovie(id: string) {
    this.router.navigate(['/edit', id]);
  }
}
