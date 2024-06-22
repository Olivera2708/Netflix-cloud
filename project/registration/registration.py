import json
import boto3
import os
from botocore.exceptions import ClientError

user_pool_id = os.environ['USER_POOL_ID']
client_id = os.environ['CLIENT_ID']

client = boto3.client('cognito-idp')

def registration(event, context):
    body = json.loads(event['body'])
    
    first_name = body['first_name']
    last_name = body['last_name']
    birthdate = body['birthdate']
    username = body['username']
    password = body['password']
    email = body['email']
    role = body.get('role', 'RegularUser')

    try:
        respones = client.sign_up(
            ClientId=client_id,
            Username=username,
            Password=password,
            UserAttributes=[
                {
                    'Name': 'email',
                    'Value': email
                },
                {
                    'Name': 'given_name',
                    'Value': first_name
                },
                {
                    'Name': 'family_name',
                    'Value': last_name
                },
                {
                    'Name': 'birthdate',
                    'Value': birthdate
                }
            ]
        )

        client.admin_add_user_to_group(
            UserPoolId=user_pool_id,
            Username=username,
            GroupName=role
        )

        return {
            'statusCode': 200,
            'body': json.dumps('User registered successfully')
        }
    except ClientError as e:
        return {
            'statusCode': 400,
            'body': json.dumps(e.response['Error']['Message']) 
        }