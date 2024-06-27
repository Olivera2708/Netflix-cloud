import { Component } from '@angular/core';
import {FormsModule} from "@angular/forms";
import {MatError, MatFormField, MatLabel} from "@angular/material/form-field";
import {MatIcon} from "@angular/material/icon";
import {MatIconButton} from "@angular/material/button";
import {MatInput} from "@angular/material/input";
import {MatLine} from "@angular/material/core";
import {MatList, MatListItem} from "@angular/material/list";
import {NgClass, NgForOf, NgIf} from "@angular/common";
import {MovieService} from "../movie.service";
import { CardModule } from 'primeng/card';
import {Router} from "@angular/router";
import {NavbarAdminComponent} from "../../navbar/navbar-admin/navbar-admin.component";
import {AuthenticationService} from "../../authentication/authentication.service";
@Component({
  selector: 'app-search-movies',
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
    NgIf,
    CardModule,
    NgClass,
    NavbarAdminComponent
  ],
  templateUrl: './search-movies.component.html',
  styleUrl: './search-movies.component.css'
})
export class SearchMoviesComponent {
  searchValue: string = ""
  movies: any[] = [];
  shownMovies: any[] = [];
  activeTab: string = 'movies';
  role: string = '';

  constructor(private router: Router, private movieService: MovieService, private authenticationService: AuthenticationService) {
    this.role = authenticationService.getRole()
  }

  ngOnInit(): void {
    this.search();
  }

  search() {
    this.movieService.searchMovie(this.searchValue).subscribe({
      next: (data) => {
        this.movies = [];
        for (let key in data) {
          if (data.hasOwnProperty(key)) {
            let value = data[key];
            this.movies.push(value);
          }
        }
        this.loadData()
      }
    })
  }

  onCardClick(id: string) {
    this.router.navigate(['/movie', id]);
  }

  editMovie(id: string) {
    this.router.navigate(['/edit', id]);
  }

  setActiveTab(tab: string) {
    this.activeTab = tab;
    this.loadData();
  }

  loadData(){
    this.shownMovies = []
    if (this.activeTab == "movies") {
      this.movies.forEach((movie: {title: string}) => {
        if (!movie.title.includes("/"))
          this.shownMovies.push(movie)
      });
    }
    else{
      this.movies.forEach((movie: {series: string, title: string}) => {
        if (movie.title.includes("/")) {
          let newMovie = JSON.parse(JSON.stringify(movie));
          newMovie.series = movie.title.split("/")[0]
          newMovie.title = movie.title.split("/")[1]
          this.shownMovies.push(newMovie)
        }
      });
      this.shownMovies.sort((a, b) => {
        if (a.series < b.series) {
          return -1;
        }
        if (a.series > b.series) {
          return 1;
        }
        if (a.title < b.title) {
          return -1;
        }
        if (a.title > b.title) {
          return 1;
        }
        return 0;
      });
      for (let index = 0; index < this.shownMovies.length; index++) {
        const movie = this.shownMovies[index];
        if (index === 0 || this.shownMovies[index - 1].series !== movie.series) {
            const newMovie = {
              series: movie.series,
              displaySeries: true
            };
            this.shownMovies.splice(index, 0, newMovie);
            index++;
        } else {
          movie.displaySeries = false;
        }
      }
    }
  }
}
