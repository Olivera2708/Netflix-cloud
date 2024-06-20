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
    NgIf
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

  constructor(private movieService: MovieService, private _snackBar: MatSnackBar) { }

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



  async onSubmit() {
    if (!this.validateForm()) {
      return;
    }
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

        this.movieService.addNewMovie(payload).subscribe({
          next: (data) => {
            if (data['message'] == "Success")
              this._snackBar.open('Movie is uploading...', 'Close');
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

  validateForm(): boolean {
    const currentYear = new Date().getFullYear();
    this.errors = '';

    if (!this.title.trim()) {
      this.errors = 'Title is required';
      return false;
    }
    if (!this.description.trim()) {
      this.errors = 'Description is required';
      return false;
    }
    if (this.genres.length === 0) {
      this.errors = 'At least one genre is required';
      return false;
    }
    if (this.actors.length === 0) {
      this.errors = 'At least one actor is required';
      return false;
    }
    if (this.directors.length === 0) {
      this.errors = 'At least one director is required';
      return false;
    }

    return true;
  }

  convertFileToBase64(file: File): Promise<string> {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.readAsDataURL(file);
      reader.onload = () => resolve(reader.result?.toString().split(',')[1] || '');
      reader.onerror = error => reject(error);
    });
  }
}
