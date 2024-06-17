import {ChangeDetectorRef, Component} from '@angular/core';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import {MatList, MatListItem} from "@angular/material/list";
import {MatIcon} from "@angular/material/icon";
import {FormsModule} from "@angular/forms";
import {NgForOf} from "@angular/common";
import {MatLine} from "@angular/material/core";
import {MatIconButton} from "@angular/material/button";
import {MatFileUploadModule} from "mat-file-upload";

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
    MatFileUploadModule
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
  movieText: string = '';
  file: File | null = null;
  title: string = '';
  description: string = '';
  year: string = '';

  constructor(private cdr: ChangeDetectorRef) { }

  addActor() {
    if (this.newActor.trim()) {
      this.actors.push(this.newActor.trim());
      this.newActor = '';
      this.cdr.detectChanges();
    }
  }

  removeActor(index: number) {
    this.actors.splice(index, 1);
  }

  addGenre() {
    if (this.newGenre.trim()) {
      this.genres.push(this.newGenre.trim());
      this.newGenre = '';
      this.cdr.detectChanges();
    }
  }

  removeGenre(index: number) {
    this.genres.splice(index, 1);
  }

  addDirector() {
    if (this.newDirector.trim()) {
      this.directors.push(this.newDirector.trim());
      this.newDirector = '';
      this.cdr.detectChanges();
    }
  }

  removeDirector(index: number) {
    this.directors.splice(index, 1);
  }

  onMovieSelected(event: any): void {
    this.file = event.target.files[0];
    if (this.file) {
      if (!this.file.name.toLowerCase().endsWith('.mp4')) {
        this.movieText = 'The selected file is not an MP4 file.';
      } else {
        this.movieText = this.file.name;
      }
    }
  }

  onSubmit(){

  }
}
