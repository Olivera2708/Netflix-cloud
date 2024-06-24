import { Component } from '@angular/core';
import { CognitoUserPool, CognitoUserAttribute, CognitoUserSession, CognitoUser } from 'amazon-cognito-identity-js';
import { FormsModule } from '@angular/forms';
import * as AWS from 'aws-sdk';


@Component({
  selector: 'app-registration',
  standalone: true,
  imports: [FormsModule],
  templateUrl: './registration.component.html',
  styleUrl: './registration.component.css'
})
export class RegistrationComponent {
  username: string = "";
  password: string = "";
  firstName: string = "";
  lastName: string = "";
  birthdate: string = "";
  email: string = "";
  role: string = "RegularUser";

  userPoolData = {
    UserPoolId: 'eu-central-1_bbiT6tV5j',
    ClientId: '2tvrm3ovd9vvchpcj5k5tq88eu'
  };

  userPool = new CognitoUserPool(this.userPoolData);

  onSubmit() {
    const attributeList = [];

    const dataFirstName = {
      Name: 'custom:first_name',
      Value: this.firstName
    };
    const dataEmail = {
      Name: 'email',
      Value: this.email
    };
    const dataLastName = {
      Name: 'custom:last_name',
      Value: this.lastName
    };
    const dataBirthdate = {
      Name: 'custom:birthdate',
      Value: this.birthdate
    };
 

    attributeList.push(new CognitoUserAttribute(dataFirstName));
    attributeList.push(new CognitoUserAttribute(dataLastName));
    attributeList.push(new CognitoUserAttribute(dataBirthdate));
    attributeList.push(new CognitoUserAttribute(dataEmail));

    this.userPool.signUp(this.username, this.password, attributeList, [], (err, result) => {
      if (err) {
        alert(err.message || JSON.stringify(err));
        return;
      }
      if(result){
        const cognitoUser = result.user;
        console.log('user name is ' + cognitoUser.getUsername());

        this.addUserToGroup(cognitoUser.getUsername(), this.role, cognitoUser);
      }
    });
  }


  addUserToGroup(username: string, groupName: string, cognitoUser: CognitoUser) {
    if (cognitoUser != null) {
      const params = {
        UserPoolId: 'eu-central-1_bbiT6tV5j',
        Username: username,
        GroupName: groupName
      };
      AWS.config.update({
        region: 'eu-central-1',
        accessKeyId: 'AKIAXYKJW5CRMX6CVE7U',
        secretAccessKey: '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'
      });
      const cognitoidentityserviceprovider = new AWS.CognitoIdentityServiceProvider();
      cognitoidentityserviceprovider.adminAddUserToGroup(params, (err: any, data: any) => {
        if (err) {
          console.log(err);
        } else {
          console.log('User added to group successfully');
        }
      });
    }
  }
}