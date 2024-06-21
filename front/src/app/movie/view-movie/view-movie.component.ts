import {Component, OnInit} from '@angular/core';
import {MovieService} from "../movie.service";

@Component({
  selector: 'app-view-movie',
  standalone: true,
  imports: [],
  templateUrl: './view-movie.component.html',
  styleUrl: './view-movie.component.css'
})
export class ViewMovieComponent implements OnInit {
  id: string = "The_Matrix.mp4_29647c78-8c49-4712-bf6e-003a24282a7c"
  title: string = ""
  description: string = ""
  actors: string = ""
  directors: string = ""
  genres: string = ""
  year: string = ""


  constructor(private movieService: MovieService) { }

  ngOnInit(): void {
    this.setInformation();
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
}
