import boto3
import json
import os

client_id = os.environ['CLIENT_ID']

client = boto3.client('cognito-idp')

def verify_user(event, context):
    body = json.loads(event['body'])

    username = body['username']
    verification_code = body['verification_code']

    try:
        response = client.confirm_sign_up(
            ClientId=client_id,
            Username=username,
            ConfirmationCode=verification_code
        )
        return {
            'statusCode': 200,
            'body': json.dumps('Account is successfully verified')
        }
    except client.exceptions.CodeMismatchException:
        return {
                'statusCode': 400,
                'body': json.dumps('The verification code is incorrect')
            }    
    except client.exceptions.ExpiredCodeException:
        return {
            'statusCode': 400,
            'body': json.dumps('The verification code has expired')
        }
    except Exception as e:
        return {
            'statusCode': 400,
            'body': json.dumps(e.response['Error']['Message']) 
        }