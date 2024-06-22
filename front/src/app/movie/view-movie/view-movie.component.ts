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
  id: string = "What_Happened_To_Monday_565d6724-6493-4d9d-a4ab-6a065b2dc59e"
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
