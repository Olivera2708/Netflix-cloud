import {AfterViewInit, Component, ElementRef, Input, OnInit, ViewChild} from '@angular/core';
import {MovieService} from "../movie.service";
import {MatMenu, MatMenuItem, MatMenuTrigger} from "@angular/material/menu";
import {MatButton} from "@angular/material/button";
import {NgForOf, NgIf} from "@angular/common";
import {MatSnackBar} from "@angular/material/snack-bar";
import {DomSanitizer, SafeResourceUrl} from "@angular/platform-browser";
import {ActivatedRoute} from "@angular/router";
import {AuthenticationService} from "../../authentication/authentication.service";
import {MatIcon} from "@angular/material/icon";
import {FormBuilder, FormGroup, FormsModule, ReactiveFormsModule, Validators} from "@angular/forms";
import {MatError, MatFormField, MatLabel} from "@angular/material/form-field";
import {MatInput} from "@angular/material/input";
import {MatRadioButton, MatRadioGroup} from "@angular/material/radio";
import {MatOption, MatSelect} from "@angular/material/select";


@Component({
  selector: 'app-view-movie',
  standalone: true,
  imports: [
    MatMenu,
    MatButton,
    MatMenuItem,
    MatMenuTrigger,
    NgIf,
    MatIcon,
    NgForOf,
    FormsModule,
    MatFormField,
    MatInput,
    MatLabel,
    MatRadioGroup,
    MatSelect,
    MatRadioButton,
    MatOption,
    ReactiveFormsModule,
    MatError
  ],
  templateUrl: './view-movie.component.html',
  styleUrl: './view-movie.component.css'
})
export class ViewMovieComponent implements OnInit, AfterViewInit {
  @ViewChild('videoPlayer') videoPlayer!: ElementRef<HTMLVideoElement>;
  id: string = ""
  title: string = ""
  subtitle: string = ""
  description: string = ""
  actors: string = ""
  directors: string = ""
  genres: string = ""
  year: string = ""
  selectedResolution = 'original';
  videoURL = "";
  role : string = '';
  genreList : any
  actorList : any
  directorList : any
  ratings:any[] = []
  alreadyRated = true
  avgRating = 0;
  suggestProc = 0;
  mostLiked : string = "";

  likeOptions = ['Actors', "Effects", "Story", "Nothing"]
  ratingForm: FormGroup;

  constructor(private fb: FormBuilder, private authService: AuthenticationService, private route: ActivatedRoute, private movieService: MovieService, private _snackBar: MatSnackBar, private authenticationService: AuthenticationService){
    this.role = authenticationService.getRole();
    this.ratingForm = this.fb.group({
      rating: [null, [Validators.required, Validators.min(1), Validators.max(5)]],
      suggest: [null, Validators.required],
      likes: [null, Validators.required]
    });
  }
  ngOnInit(): void {
    this.route.paramMap.subscribe(params => {
      this.id = params.get('id') || '';
      this.setInformation();
    });

    let video = document.getElementById('video');
    if (video != null && this.role === 'Admin') {
      video.setAttribute('controlsList', 'nodownload');
    }
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
        this.genreList = data.genres;
        this.directorList = data.directors;
        this.actorList = data.actors;
        this.genres = data.genres.join(", ")
        this.actors = data.actors.join(", ")
        this.directors = data.directors.join(", ")
      }
    })
    this.authenticationService.getCurrentUserEmail().then(email => {
      this.movieService.getRating(email, this.id).subscribe({
        next: (ratings) => {
          this.alreadyRated = ratings.alreadyRated;
          this.avgRating = ratings.avgRating.toFixed(2);
          this.suggestProc = ratings.suggestProc.toFixed(0);
          this.mostLiked = ratings.mostLiked;
        }
      });
    });
  }

  getName(resolution : string) : string {
    switch (resolution){
      case "360p": return "640_360"
      case "480p": return "854_480"
      case "720p": return "1280_720"
      default: return "original"
    }
  }

  subscribeTo(forUpdate: string, value: any) {
    this.authenticationService.getCurrentUserEmail().then(email => {
      const body = {
        user_id: email,
        for_update: "subscriptions",
        payload: {
          command: "add",
          for_update: forUpdate,
          value: value
        }
      }
      this.movieService.editUser(body).subscribe({
        next: (data) => {
          // console.log(data);
        }
      });

    }).catch(error => {
      console.error('Error fetching user email:', error);
    });
  }

  submitRating() {
    if (this.ratingForm.valid) {
      this.authenticationService.getCurrentUserEmail().then(email => {
        let data = {
          "id": email,
          "movie_id": this.id,
          "rating": this.ratingForm.value.rating,
          "suggest": this.ratingForm.value.suggest,
          "likes": this.ratingForm.value.likes,
          "genres": this.genres
        }

        this.movieService.addRating(data).subscribe({
          next: (val) => {
            if (val["message"] == "success") {
              this._snackBar.open("Rating submitted!", "Close")
              this.alreadyRated = true;
            }
            else
              this._snackBar.open("There was an error!", "Close")
          }
        })
      });
    }
  }
}
