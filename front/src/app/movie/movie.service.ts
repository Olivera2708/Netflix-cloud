import {Injectable} from "@angular/core";
import {HttpClient} from "@angular/common/http";
import {Observable} from "rxjs";
import {environment} from "../../env";


@Injectable({
  providedIn: 'root'
})
export class MovieService {
  constructor(private httpClient: HttpClient) { }

  addNewMovie(data: any): Observable<any> {
    return this.httpClient.post<any>(environment.apiGateway + "update", data)
  }
}
