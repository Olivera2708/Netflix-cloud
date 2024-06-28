import {ChangeDetectorRef, Component} from '@angular/core';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import {MatList, MatListItem} from "@angular/material/list";
import {MatIcon} from "@angular/material/icon";
import {FormsModule} from "@angular/forms";
import {NgForOf, NgIf} from "@angular/common";
import {MatLine} from "@angular/material/core";
import {MatIconButton} from "@angular/material/button";
import {MatFileUploadModule} from "mat-file-upload";
import {MovieService} from "../movie.service";
import {MatSnackBar} from "@angular/material/snack-bar";
import {MatCheckbox} from "@angular/material/checkbox";

@Component({
  selector: 'app-add-movie',
  standalone: true,
  imports: [
    MatFormFieldModule,
    MatInputModule,
    MatListItem,
    MatList,
    MatIcon,
    FormsModule,
    NgForOf,
    MatLine,
    MatIconButton,
    MatFileUploadModule,
    NgIf,
    MatCheckbox
  ],
  templateUrl: './add-movie.component.html',
  styleUrls: ['./add-movie.component.css']
})
export class AddMovieComponent {
  actors: string[] = [];
  newActor: string = '';
  genres: string[] = [];
  newGenre: string = '';
  directors: string[] = [];
  newDirector: string = '';
  file: File | null = null;
  title: string = '';
  movieText: string = '';
  description: string = '';
  year: string = '';
  errors: string = '';
  checkbox: boolean = false;
  seriesName: string = "";

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

  onMovieSelected(event: any): void {
    this.file = event.target.files[0];
    if (this.file)
        this.movieText = this.file.name;
  }

  async onSubmit(event: Event) {
    event.preventDefault();
    if (!this.validateForm()) {
      return;
    }
    if (this.file != null) {
      try {
        const base64 = await this.convertFileToBase64(this.file);
        let title_name: string;
        this.title = this.title.replace("/", "_")
        if (this.checkbox)
          title_name = this.seriesName + "/" + this.title;
        else
          title_name = this.title;
        const payload = {
          file_name: this.file?.name,
          file_content: base64,
          metadata: {
            title: title_name,
            description: this.description,
            actors: this.actors,
            directors: this.directors,
            genres: this.genres,
            year: this.year
          }
        }

        this.actors = [];
        this.newActor = '';
        this.genres = [];
        this.newGenre = '';
        this.directors = [];
        this.newDirector = '';
        this.file = null;
        this.title = '';
        this.movieText= '';
        this.description = '';
        this.year = '';
        this.errors = '';
        this.seriesName = '';

        this.movieService.addNewMovie(payload).subscribe({
          next: (data) => {
            if (data['message'] == "Success")
              this._snackBar.open('Movie is uploading...', 'Close');
            else
              this._snackBar.open('There was an error while adding movie', 'Close');
          }
        })
      } catch (error) {
        this._snackBar.open('There is an error while converting file', 'Close');
      }
    }
    else {
      this.movieText = 'Select movie';
    }
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
    if (this.checkbox && !this.seriesName.trim()) {
      this.errors = 'Series name is required';
      return false;
    }
    if (!this.year.trim()) {
      this.errors = 'Year is required';
      return false;
    } else if (!/^\d{4}$/.test(this.year.trim())) {
      this.errors = 'Year must be a valid 4-digit number';
      return false;
    } else {
      const yearNumber = parseInt(this.year, 10);
      if (yearNumber > currentYear) {
        this.errors = 'Year must be in the past';
        return false;
      }
      if (yearNumber < 1900){
        this.errors = 'Year must be greater than 1900';
        return false;
      }
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

  checkboxChanged(event: boolean){
    this.checkbox = event
    if (!this.checkbox)
      this.seriesName = ''
  }
}
