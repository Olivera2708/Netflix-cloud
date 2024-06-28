import { Component, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { CognitoUserPool, AuthenticationDetails, CognitoUser } from 'amazon-cognito-identity-js';
import { AuthenticationService } from '../authentication.service';
import {environment} from "../../../env";
import { Router } from '@angular/router';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [FormsModule],
  templateUrl: './login.component.html',
  styleUrl: './login.component.css'
})
export class LoginComponent {
  loginUsername: string = "";
  loginPassword: string = "";

  constructor(private authenticationService: AuthenticationService, private router: Router) {}

  userPoolData = {
    UserPoolId: environment.UserPoolId,
    ClientId: environment.ClientId
  };

  userPool = new CognitoUserPool(this.userPoolData);

  onLogin() {
    const authenticationData = {
      Username: this.loginUsername,
      Password: this.loginPassword
    };

    const authenticationDetails = new AuthenticationDetails(authenticationData);

    const userData = {
      Username: this.loginUsername,
      Pool: this.userPool
    };

    const cognitoUser = new CognitoUser(userData);

    cognitoUser.authenticateUser(authenticationDetails, {
      onSuccess: (result) => {
        this.authenticationService.login(result);

        this.router.navigate(['/search'])
        },
      onFailure: (err) => {
        alert(err.message || JSON.stringify(err));
      }
    });
  }

  redirectToRegistration() {
    this.router.navigate(['/registration'])
  }
}
