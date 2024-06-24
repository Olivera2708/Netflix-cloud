import {AfterViewInit, Component, ElementRef, OnInit, ViewChild} from '@angular/core';
import {MovieService} from "../movie.service";
import {MatMenu, MatMenuItem, MatMenuTrigger} from "@angular/material/menu";
import {MatButton} from "@angular/material/button";
import {NgIf} from "@angular/common";
import {MatSnackBar} from "@angular/material/snack-bar";

@Component({
  selector: 'app-view-movie',
  standalone: true,
  imports: [
    MatMenu,
    MatButton,
    MatMenuItem,
    MatMenuTrigger,
    NgIf
  ],
  templateUrl: './view-movie.component.html',
  styleUrl: './view-movie.component.css'
})
export class ViewMovieComponent implements OnInit, AfterViewInit {
  @ViewChild('videoPlayer') videoPlayer!: ElementRef<HTMLVideoElement>;
  id: string = "Avenger_Endgame_d64aff03-b1d6-4b95-aa3f-99e019ddc9e3"
  title: string = ""
  subtitle: string = ""
  description: string = ""
  actors: string = ""
  directors: string = ""
  genres: string = ""
  year: string = ""
  selectedResolution = 'original';
  videoURL = "";

  constructor(private movieService: MovieService, private _snackBar: MatSnackBar){}
  ngOnInit(): void {
    this.setInformation();
  }

  ngAfterViewInit(): void {
    this.getVideo(`${this.id}/original.mp4`);
  }

  getVideo(key: string) {
    this.movieService.getMovieURL(key).subscribe({
      next: (data) => {
        this.videoURL = data['url']
        this.videoPlayer.nativeElement.src = this.videoURL;
        this.videoPlayer.nativeElement.load();
      }
    })
  }

  changeResolution(resolution: string) {
    this.selectedResolution = resolution;
    this.getVideo(`${this.id}/${this.getName(resolution)}.mp4`)
  }

  setInformation(){
    this.movieService.getMetadata(this.id).subscribe({
      next: (data) => {
        if (data.title.includes("/")){
          this.title = data.title.split("/")[1]
          this.subtitle = data.title.split("/")[0]
        }
        else{
          this.title = data.title
        }
        this.description = data.description
        this.year = data.year
        this.genres = data.genres.join(", ")
        this.actors = data.actors.join(", ")
        this.directors = data.directors.join(", ")
      }
    })
  }

  getName(resolution : string) : string {
    switch (resolution){
      case "360p": return "640_360"
      case "480p": return "854_480"
      case "720p": return "1280_720"
      default: return "original"
    }
  }
}
