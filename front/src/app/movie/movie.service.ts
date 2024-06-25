import {Injectable} from "@angular/core";
import {HttpClient, HttpParams} from "@angular/common/http";
import {Observable} from "rxjs";
import {environment} from "../../env";
import {Metadata} from "./model/metadata.model";


@Injectable({
  providedIn: 'root'
})
export class MovieService {
  constructor(private httpClient: HttpClient) { }

  addNewMovie(data: any): Observable<any> {
    return this.httpClient.post<any>(environment.apiGateway + "upload", data,
      {'headers': {'Content-Type': 'application/json'}})
  }

  editMetadata(data: any): Observable<any> {
    return this.httpClient.put<any>(environment.apiGateway + "metadata", data,
      {'headers': {'Content-Type': 'application/json'}})
  }

  getMovieURL(key: string): Observable<any> {
    return this.httpClient.get<any>(environment.apiGateway + "movie" + "?bucket=movies-team3&key=" + key,
      {'headers': {'Content-Type': 'application/json'}})
  }

  searchMovie( actors: string[], directors: string[], genres: string[],title: string, description: string): Observable<any> {

    return this.httpClient.post<any>(`${environment.apiGateway}search`,
      {title: title,
            description: description,
            genres: genres,
            actors: actors,
            directors: directors},
      {'headers' : { 'Content-Type': 'application/json' },}
    );
  }
  getMetadata(id: string): Observable<Metadata> {
    return this.httpClient.get<Metadata>(environment.apiGateway + "metadata?id=" + id,
      {'headers': {'Content-Type': 'application/json'}})
  }

  deleteMovie(id: string): Observable<any> {
    return this.httpClient.delete<any>(environment.apiGateway + "movie/" + id,
      {'headers': {'Content-Type': 'application/json'}})
  }

  editUser(data: any): Observable<any> {
    return this.httpClient.put<any>(environment.apiGateway + "feed", data,
      {'headers': {'Content-Type': 'application/json'}})
  }
}
