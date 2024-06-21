import {Injectable} from "@angular/core";
import {HttpClient} from "@angular/common/http";
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

  downloadMovie(key: string): Observable<any> {
    return this.httpClient.get<any>(environment.apiGateway + "download" + "?bucket=movie-team3&key=" + key,
      {'headers': {'Content-Type': 'application/json'}})
  }

  getMetadata(id: string): Observable<Metadata> {
    return this.httpClient.get<Metadata>(environment.apiGateway + "metadata?id=" + id,
      {'headers': {'Content-Type': 'application/json'}})
  }
}
