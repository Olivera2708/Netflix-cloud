import { Component, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { CognitoUserPool, AuthenticationDetails, CognitoUser } from 'amazon-cognito-identity-js';
import { AuthenticationService } from '../authentication.service';

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

  constructor(private authenticationService: AuthenticationService) {}

  userPoolData = {
    UserPoolId: 'eu-central-1_bbiT6tV5j',
    ClientId: '2tvrm3ovd9vvchpcj5k5tq88eu'
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
        console.log('Access token: ' + result.getAccessToken().getJwtToken());

        // Ovdje možete dodati logiku za redirekciju ili druge akcije nakon uspješnog logina

        this.authenticationService.login(result);
      },
      onFailure: (err) => {
        alert(err.message || JSON.stringify(err));
      }
    });
  }  
}
          
          // constructor() { }
          
          // ngOnInit(): void {
            //   this.login();
            
            // }
            
            // login(): void {
              //   window.location.href = `https://moviefy.auth.eu-central-1.amazoncognito.com/login?response_type=code&client_id=2tvrm3ovd9vvchpcj5k5tq88eu&redirect_uri=http://localhost:4200/search`;
              //   // Zamijenite 'your_domain', 'your_region', 'your_user_pool_client_id' i 'http://localhost:4200' sa vašim stvarnim podacima
              // }



              // private userPool = new CognitoUserPool({
              //   UserPoolId: 'eu-central-1_cZJlFs8hO',
              //   ClientId: '2gm305pi2b2ch59dnkme2oogrf'
              // });
            
              // constructor() { }
            
              // login(username: string, password: string): void {
              //   const authenticationData = {
              //     Username: username,
              //     Password: password
              //   };
              //   const authenticationDetails = new AuthenticationDetails(authenticationData);
              //   const userData = {
              //     Username: username,
              //     Pool: this.userPool
              //   };
            
              //   const cognitoUser = new CognitoUser(userData);
            
              //   cognitoUser.authenticateUser(authenticationDetails, {
              //     onSuccess: function (result) {
              //       console.log('Login successful!', result);
              //       // Handle successful login (e.g., redirect to dashboard)
              //     },
              //     onFailure: function (err) {
              //       console.error('Error during login:', err);
              //       // Handle login error
              //     }
              //   });
              // }
