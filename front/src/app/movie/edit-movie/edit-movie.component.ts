import {ChangeDetectorRef, Component, OnInit} from '@angular/core';
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
import {ActivatedRoute, Router} from "@angular/router";

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
  templateUrl: './edit-movie.component.html',
  styleUrls: ['./edit-movie.component.css']
})
export class EditMovieComponent implements OnInit {
  id: string = "";
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

  constructor(private route: ActivatedRoute, private movieService: MovieService, private _snackBar: MatSnackBar, private router: Router) { }

  ngOnInit(): void {
    this.route.paramMap.subscribe(params => {
      this.id = params.get('id') || '';
      this.getInitialData();
    });
  }

  getInitialData(){
    this.movieService.getMetadata(this.id).subscribe({
      next: (data) => {
        this.setTitle(data["title"])
        this.description = data["description"]
        this.year = data["year"]
        this.actors = data["actors"]
        this.directors = data["directors"]
        this.genres = data["genres"]
      }
    })
  }

  setTitle(data: string){
    if (data.includes("/")){
      const split_data = data.split("/")
      this.seriesName = split_data[0]
      this.title = split_data[1]
      this.checkbox = true;
    }
    else{
      this.title = data;
      this.checkbox = false;
    }
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

    let title_name: string;
    this.title = this.title.replace("/", "_")
    if (this.checkbox)
      title_name = this.seriesName + "/" + this.title;
    else
      title_name = this.title;

    const payload : Payload = {
      id: this.id,
      metadata: {
        title: title_name,
        description: this.description,
        actors: this.actors,
        directors: this.directors,
        genres: this.genres,
        year: this.year
      }
    }

    if (this.file != null) {
      try {
        const base64 = await this.convertFileToBase64(this.file);
        payload.file_name = this.file?.name ?? '';
        payload.file_content = base64;

        this.movieService.addNewMovie(payload).subscribe({
          next: (data) => {
            if (data['message'] == "Success") {
              this._snackBar.open('Movie is uploading...', 'Close');
              this.router.navigate(['/search']);
            }
            else
              this._snackBar.open('There was an error while uploading movie', 'Close');
          }
        })
      }
      catch (error) {
        this._snackBar.open('There is an error while converting file', 'Close');
      }
    }
    else {
      this.movieService.editMetadata(payload).subscribe({
        next: (data) => {
          if (data['message'] == "Success")
            this._snackBar.open('Change is successful!', 'Close');
          else
            this._snackBar.open('There was an error while adding movie', 'Close');
        }
      })
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
    if (!this.checkbox)
      this.seriesName = ''
  }

  deleteMovie(){
    this.movieService.deleteMovie(this.id).subscribe({
      next: (data) => {
        this.router.navigate(['/search']);
      }
    })
  }
}

interface Payload {
  id: string;
  metadata: {
    title: string;
    description: string;
    actors: string[];
    directors: string[];
    genres: string[];
    year: string;
  };
  file_name?: string;
  file_content?: string;
}
