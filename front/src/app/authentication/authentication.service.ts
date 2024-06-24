import { Injectable } from '@angular/core';
import { AuthenticationDetails, CognitoUser, CognitoUserAttribute, CognitoUserPool, CognitoUserSession } from 'amazon-cognito-identity-js';
import { JwtHelperService } from "@auth0/angular-jwt";
import { BehaviorSubject, Observable } from 'rxjs';
import { HttpClient } from '@angular/common/http';

@Injectable({
  providedIn: 'root'
})
export class AuthenticationService {
  private userPoolId = 'eu-central-1_cZJlFs8hO';
  private clientId = '2gm305pi2b2ch59dnkme2oogrf';
  private userPool = new CognitoUserPool({
    UserPoolId: this.userPoolId,
    ClientId: this.clientId
  });

  constructor(private httpClient: HttpClient) { }

  signUp(username: string, password: string, email: string): Promise<any> {
    const attributeList = [
      new CognitoUserAttribute({ Name: 'email', Value: email })
    ];

    return new Promise((resolve, reject) => {
      this.userPool.signUp(username, password, attributeList, [], (err, result) => {
        if (err) {
          reject(err);
          return;
        }
        if(result)
          resolve(result.user);
      });
    });
  }

  signIn(username: string, password: string): Promise<any> {
    const authenticationData = {
      Username: username,
      Password: password
    };
    const authenticationDetails = new AuthenticationDetails(authenticationData);
    const userData = {
      Username: username,
      Pool: this.userPool
    };

    const cognitoUser = new CognitoUser(userData);

    return new Promise((resolve, reject) => {
      cognitoUser.authenticateUser(authenticationDetails, {
        onSuccess: result => {
          resolve(result);
        },
        onFailure: err => {
          reject(err);
        }
      });
    });
  }

  signOut(): void {
    const cognitoUser = this.userPool.getCurrentUser();
    if (cognitoUser) {
      cognitoUser.signOut();
    }
  }

  user$: BehaviorSubject<string> = new BehaviorSubject("");
  userState: Observable<string> = this.user$.asObservable();

  login(result: CognitoUserSession) {
    localStorage.setItem('accessToken', result.getAccessToken().getJwtToken());
    localStorage.setItem('idToken', result.getIdToken().getJwtToken());
    localStorage.setItem('refreshToken', result.getRefreshToken().getToken());

    this.setUser();
  }

  isLoggedIn(): boolean {
    return localStorage.getItem('accessToken') != null;
  }

  getRole(): string {
    if (this.isLoggedIn()) {
      const accessToken: any = localStorage.getItem('accessToken');
      const helper: JwtHelperService = new JwtHelperService();
      return helper.decodeToken(accessToken).role;
    }
    return '';
  }

  getUserId(): number {
    if (this.isLoggedIn()) {
      const accessToken: any = localStorage.getItem('accessToken');
      const helper: JwtHelperService = new JwtHelperService();
      return helper.decodeToken(accessToken).id
    }
    return -1;
  }

  setUser(): void {
    this.user$.next(this.getRole());
  }

  logout(): void {
    this.user$.next('');
    localStorage.removeItem('accessToken');
    // this.httpClient.get(environment.apiHost + "users/logout");
  }
}
