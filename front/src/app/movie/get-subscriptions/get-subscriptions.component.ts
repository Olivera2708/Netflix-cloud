import { Component } from '@angular/core';
import {FormsModule} from "@angular/forms";
import {MatError, MatFormField, MatLabel} from "@angular/material/form-field";
import {MatIcon} from "@angular/material/icon";
import {MatIconButton} from "@angular/material/button";
import {MatInput} from "@angular/material/input";
import {MatLine} from "@angular/material/core";
import {MatList, MatListItem} from "@angular/material/list";
import {NgForOf, NgIf} from "@angular/common";
import {ActivatedRoute, Router} from "@angular/router";
import {MovieService} from "../movie.service";
import {MatSnackBar} from "@angular/material/snack-bar";
import {AuthenticationService} from "../../authentication/authentication.service";

@Component({
  selector: 'app-get-subscriptions',
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
  templateUrl: './get-subscriptions.component.html',
  styleUrl: './get-subscriptions.component.css'
})
export class GetSubscriptionsComponent {
  actors: string[] = [];
  newActor: string = '';
  genres: string[] = [];
  newGenre: string = '';
  directors: string[] = [];
  newDirector: string = '';
  errors: string = '';
  role: string = '';

  constructor(private snackBar: MatSnackBar, private route: ActivatedRoute, private movieService: MovieService, private _snackBar: MatSnackBar, private authenticationService: AuthenticationService){
    this.role = authenticationService.getRole()
  }

  ngOnInit(): void {
    this.loadSubscriptions();
  }

  addActor() {
    if (this.newActor.trim()) {
      this.actors.push(this.newActor.trim());
      this.subscribeTo('actors', this.newActor.trim())
      this.newActor = '';
    }
  }

  removeActor(index: number) {
    this.unsubscribeFrom('actors', this.actors[index])
    // this.actors.splice(index, 1);
  }

  addGenre() {
    if (this.newGenre.trim()) {
      this.genres.push(this.newGenre.trim());
      this.subscribeTo('genres', this.newGenre.trim())
      this.newGenre = '';
    }
  }

  removeGenre(index: number) {
    this.unsubscribeFrom('genres', this.genres[index])
    // this.genres.splice(index, 1);
  }

  addDirector() {
    if (this.newDirector.trim()) {
      this.directors.push(this.newDirector.trim());
      this.subscribeTo('directors', this.newDirector.trim())
      this.newDirector = '';
    }
  }

  removeDirector(index: number) {
    this.unsubscribeFrom('directors', this.directors[index])
    // this.directors.splice(index, 1);
  }

  subscribeTo(forUpdate: string, value: any) {
    this.authenticationService.getCurrentUserEmail().then(email => {
      const body = {
        user_id: email,
        payload: {
          for_update: forUpdate,
          value: value
        }
      }
      this.movieService.addSubscription(body).subscribe({
        next: (data) => {
          this.showAlert('You subscribed to '+forUpdate+': '+value, 'Close');
        }
      });

    }).catch(error => {
      console.error('Error fetching user email:', error);
    });
  }
  unsubscribeFrom(forUpdate: string, value: any) {
    this.authenticationService.getCurrentUserEmail().then(email => {
      const body = {
        user_id: email,
        payload: {
          for_update: forUpdate,
          value: value
        }
      }
      this.movieService.deleteSubscription(body).subscribe({
        next: (data) => {
          this.showAlert('You unsubscribed from '+forUpdate+': '+value, 'Close');
          this.loadSubscriptions();
        },
        error: (error) => {
          this.showAlert(error.error.error, 'Close');
        }
      });

    }).catch(error => {
      console.error('Error fetching user email:', error);
    });
  }

  showAlert(message: string, action: string = '', duration: number = 3000): void {
    this.snackBar.open(message, action, {
      duration: duration,
    });
  }

  private loadSubscriptions() {
    this.authenticationService.getCurrentUserEmail().then(email => {
      this.movieService.getSubscriptions(email).subscribe({
        next: (response) => {
          const subscriptions = this.convertStringToJson(response);

          this.genres = subscriptions['genres'];
          this.directors = subscriptions['directors']
          this.actors = subscriptions['actors']
        }
      })
    });
  }

  convertStringToJson(str: string) {
    // Replace single quotes with double quotes
    const jsonCompatibleString = str.replace(/'/g, '"');

    // Parse the modified string as JSON
    try {
      return JSON.parse(jsonCompatibleString);
      // this.jsonString = JSON.stringify(this.jsonObject, null, 2); // Prettify JSON string
    } catch (error) {
      console.error('Invalid JSON string', error);
    }
  }
}
