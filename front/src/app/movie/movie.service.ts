import {Injectable} from "@angular/core";
import {HttpClient, HttpParams} from "@angular/common/http";
import {Observable} from "rxjs";
import {environment} from "../../env";


@Injectable({
  providedIn: 'root'
})
export class MovieService {
  constructor(private httpClient: HttpClient) { }

  addNewMovie(data: any): Observable<any> {
    return this.httpClient.post<any>(environment.apiGateway + "upload", data,
      {'headers': {'Content-Type': 'application/json'}})
  }

  downloadMovie(key: string): Observable<any> {
    return this.httpClient.get<any>(environment.apiGateway + "download" + "?bucket=movie-team3&key=" + key,
      {'headers': {'Content-Type': 'application/json'}})
  }

  searchMovie( actors: string[], directors: string[], genres: string[],title: string, description: string): Observable<any> {
    let params = new HttpParams();

      params = params.append('title', title);


      params = params.append('description', description);

    actors.forEach(actor => {
      params = params.append('actors', actor);
    });

    directors.forEach(director => {
      params = params.append('directors', director);
    });

    genres.forEach(genre => {
      params = params.append('genres', genre);
    });

    return this.httpClient.get<any>(`${environment.apiGateway}search`, {
      headers: { 'Content-Type': 'application/json' },
      params: params
    });
  }
}
