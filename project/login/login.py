import json
import boto3
import os
from botocore.exceptions import ClientError

client_id = os.environ['CLIENT_ID']

client = boto3.client('cognito-idp')

def login(event, context):
    body = json.loads(event['body'])
    
    username = body['username']
    password = body['password']

    try:
        response = client.initiate_auth(
            ClientId=client_id,
            AuthFlow='USER_PASSWORD_AUTH',
            AuthParameters={
                'USERNAME': username,
                'PASSWORD': password
            }
        )
        return {
            'statusCode': 200,
            'body': json.dumps(response['AuthenticationResult'])
        }
    except ClientError as e:
        return {
            'statusCode': 400,
            'body': json.dumps(e.response['Error']['Message'])
        }