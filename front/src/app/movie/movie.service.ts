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
    return this.httpClient.get<any>(environment.apiGateway + "movie" + "?key=" + key,
      {'headers': {'Content-Type': 'application/json'}})
  }

  searchMovie(data: string): Observable<any> {
    return this.httpClient.get<any>(`${environment.apiGateway}search?value=` + data,
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

  addRating(data: any): Observable<any> {
    return this.httpClient.post<any>(environment.apiGateway + "rating", data,
      {'headers': {'Content-Type': 'application/json'}})
  }

  getRating(user_email: string, movie_id: string): Observable<any> {
    return this.httpClient.get<any>(environment.apiGateway + "rating?user_id=" + user_email + "&movie_id=" + movie_id,
      {'headers': {'Content-Type': 'application/json'}})
  }

  addDownloadedGenre(data: any): Observable<any> {
    return this.httpClient.post<any>(environment.apiGateway + "feed/downloaded", data,
      {'headers': {'Content-Type': 'application/json'}})
  }

  getSubscriptions(userId: string): Observable<any> {
    return this.httpClient.get<any>(environment.apiGateway + "subscriptions?id=" + userId,
      {'headers': {'Content-Type': 'application/json'}})
  }

  addSubscription(data: any): Observable<any> {
    return this.httpClient.put<any>(environment.apiGateway + "subscriptions", data,
      {'headers': {'Content-Type': 'application/json'}})
  }

  deleteSubscription(data: any): Observable<any> {
    return this.httpClient.delete<any>(environment.apiGateway + "subscriptions", { body: data })
  }

  feedMovie(id: string): Observable<any> {
    return this.httpClient.get<any>(environment.apiGateway + "feed?id=" + id,
      {'headers' : { 'Content-Type': 'application/json' },}
    );
  }
}
