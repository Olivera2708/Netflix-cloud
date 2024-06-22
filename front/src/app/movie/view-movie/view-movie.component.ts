import {Component, OnInit} from '@angular/core';
import {MovieService} from "../movie.service";
import {MatMenu, MatMenuItem, MatMenuTrigger} from "@angular/material/menu";
import {MatButton} from "@angular/material/button";

@Component({
  selector: 'app-view-movie',
  standalone: true,
  imports: [
    MatMenu,
    MatButton,
    MatMenuItem,
    MatMenuTrigger
  ],
  templateUrl: './view-movie.component.html',
  styleUrl: './view-movie.component.css'
})
export class ViewMovieComponent implements OnInit {
  id: string = "What_Happened_To_Monday_565d6724-6493-4d9d-a4ab-6a065b2dc59e"
  title: string = ""
  description: string = ""
  actors: string = ""
  directors: string = ""
  genres: string = ""
  year: string = ""
  selectedResolution = 'original';

  constructor(private movieService: MovieService) { }

  ngOnInit(): void {
    this.setInformation();
  }

  changeResolution(resolution: string) {
    this.selectedResolution = resolution;
  }
  setInformation(){
    this.movieService.getMetadata(this.id).subscribe({
      next: (data) => {
        this.title = data.title
        this.description = data.description
        this.year = data.year
        this.genres = data.genres.join(", ")
        this.actors = data.actors.join(", ")
        this.directors = data.directors.join(", ")
      }
    })
  }

  menuItemClicked(item: string) {
    console.log(`${item} clicked`);
  }
}
