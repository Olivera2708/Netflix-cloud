import json
import boto3
import base64
import uuid
from botocore.exceptions import NoCredentialsError

s3 = boto3.client('s3')

def upload_movie(event, context):
    try:
        event = json.loads(event["body"])
        key = event["id"]
        file_content_base64 = event['file_content']
        file_content = base64.b64decode(file_content_base64)

        bucket = 'movies-team3'
        s3.put_object(Bucket=bucket, Key=key, Body=file_content)

        return {
            'statusCode': 200,
            'body': json.dumps('File uploaded')
        }

    except NoCredentialsError:
        return {
            'statusCode': 403,
            'body': json.dumps('Credentials not available')
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps(str(e))
        }