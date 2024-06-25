import { Injectable } from '@angular/core';
import { AuthenticationDetails, CognitoRefreshToken, CognitoUser, CognitoUserAttribute, CognitoUserPool, CognitoUserSession } from 'amazon-cognito-identity-js';
import { JwtHelperService } from "@auth0/angular-jwt";
import { BehaviorSubject, Observable } from 'rxjs';
import { HttpClient } from '@angular/common/http';
import { environment } from "../../env";
import {Metadata} from "../movie/model/metadata.model";

@Injectable({
  providedIn: 'root'
})
export class AuthenticationService {
  private userPoolId = environment.UserPoolId;
  private clientId = environment.ClientId;
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
      this.logout();
    }
  }

  refreshAuthToken() {
    const refreshToken = localStorage.getItem('refreshToken');
    const cognitoUser = this.userPool.getCurrentUser();
    if(cognitoUser && refreshToken){
      const refreshToken2 = new CognitoRefreshToken({RefreshToken: refreshToken})
      return new Promise<void>((resolve, reject) => {
        cognitoUser.refreshSession(refreshToken2, (err, session) => {
          if (err) {
            console.log(err);
            reject(err);
            return;
          }

          const newAccessToken = session.getAccessToken().getJwtToken();
          const newIdToken = session.getIdToken().getJwtToken();
          localStorage.setItem('accessToken', newAccessToken);
          localStorage.setItem('idToken', newIdToken);
          resolve();
        });
      });
    } else {
      return Promise.reject(new Error("No valid user or refresh token found"));
    }
  }

  isTokenValid() {
    const token = localStorage.getItem('idToken');
    if (!token) {
      return false;
    }
    const tokenPayload = JSON.parse(atob(token.split('.')[1]));
    const expiry = tokenPayload.exp * 1000;
    return expiry > Date.now();
  }

  async makeAuthenticatedRequest2(){
    if (!this.isTokenValid()) {
      try {
        await this.refreshAuthToken();
      } catch (error) {
        console.log('Failed to refresh tokens', error);
        this.logout()
        return null;
      }
    }
    return localStorage.getItem('idToken');
  }

  async makeAuthenticatedRequest(apiUrl: string) {
    if (!this.isTokenValid()) {
      await this.refreshAuthToken();
    }
    const token = localStorage.getItem('accessToken');
    fetch(apiUrl, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
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
      const decodedToken = helper.decodeToken(accessToken);
      if (decodedToken && decodedToken['cognito:groups']) {
        return decodedToken['cognito:groups'][0];
      }
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
    localStorage.removeItem('idToken');
    localStorage.removeItem('refreshToken');
    // this.httpClient.get(environment.apiHost + "users/logout");
  }

  uploadUser(id: string): Observable<any> {
    return this.httpClient.post<any>(environment.apiGateway + "feed",
      {"id":id },
      {'headers': {'Content-Type': 'application/json'}})
  }

  getCurrentUserEmail(): Promise<string> {
    return new Promise((resolve, reject) => {
      const cognitoUser = this.userPool.getCurrentUser();
      if (cognitoUser) {
        cognitoUser.getSession((err: any, session: any) => {
          if (err) {
            reject(err);
            return;
          }

          cognitoUser.getUserAttributes((err, attributes) => {
            if (err) {
              reject(err);
              return;
            }
            if (attributes == undefined) return;
            const emailAttribute = attributes.find(attr => attr.Name === 'email');
            if (emailAttribute) {
              resolve(emailAttribute.Value);
            } else {
              reject(new Error('Email attribute not found'));
            }
          });
        });
      } else {
        reject(new Error('No user is currently authenticated'));
      }
    });
  }
}
