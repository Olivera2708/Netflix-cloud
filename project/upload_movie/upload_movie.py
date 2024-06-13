import json
import boto3
import base64
from botocore.exceptions import NoCredentialsError
s3 = boto3.client('s3')

def upload_movie(event, context):
    try:
        s3_key = event["key"]
        s3_bucket = event["bucket"]

        response = s3.get_object(Bucket=s3_bucket, Key=s3_key)
        json_data = response['Body'].read().decode('utf-8')
        data = json.loads(json_data)

        key = data["id"]
        file_content_base64 = data['file_content']
        file_content = base64.b64decode(file_content_base64)

        bucket = 'movies-team3'
        s3.put_object(Bucket=bucket, Key=key, Body=file_content)

        return event
    
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