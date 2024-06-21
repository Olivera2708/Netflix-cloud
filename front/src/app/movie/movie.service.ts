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

    return this.httpClient.post<any>(`${environment.apiGateway}search`,
      {title: title,
            description: description,
            genres: genres,
            actors: actors,
            directors: directors},
      {headers : { 'Content-Type': 'application/json' },}
    );
  }
}
