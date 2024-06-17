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
    NgIf
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
  errors: any = {};

  constructor(private movieService: MovieService) { }

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

  async onSubmit() {
    // this.movieService.downloadMovie('What_Happened_To_Monday_63c48b80-2a88-4009-a72d-07a1be4a298e/original.mp4').subscribe({
    //   next: (data) => {
    //     console.log(data)
    //   }
    // })
    if (!this.validateForm()) {
      return;
    }
    if (this.file != null) {
      try {
        const base64 = await this.convertFileToBase64(this.file);

        const payload = {
          file_name: this.file?.name,
          file_content: base64,
          metadata: {
            title: this.title,
            description: this.description,
            actors: this.actors,
            directors: this.directors,
            genres: this.genres,
            year: this.year
          }
        }

        this.movieService.addNewMovie(payload).subscribe({
          next: (data) => {
            console.log(data)
          }
        })
      } catch (error) {
        console.error('Error converting file to base64:', error);
      }
    }
  }

  validateForm(): boolean {
    const currentYear = new Date().getFullYear();
    this.errors = {};

    if (!this.title.trim()) {
      this.errors.title = 'Title is required';
    }
    if (!this.description.trim()) {
      this.errors.description = 'Description is required';
    }
    if (!this.year.trim()) {
      this.errors.year = 'Year is required';
    } else if (!/^\d{4}$/.test(this.year.trim())) {
      this.errors.year = 'Year must be a valid 4-digit number';
    } else {
      const yearNumber = parseInt(this.year, 10);
      if (yearNumber > currentYear || yearNumber < 1900) {
        this.errors.year = 'Year must be in the past';
      }
    }
    if (this.genres.length === 0) {
      this.errors.genres = 'At least one genre is required';
    }
    if (this.actors.length === 0) {
      this.errors.actors = 'At least one actor is required';
    }
    if (this.directors.length === 0) {
      this.errors.directors = 'At least one director is required';
    }
    if (this.file == null){
      this.errors.file = 'No file selected'
    }

    console.log(this.errors)
    return Object.keys(this.errors).length === 0;
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
