import json
import boto3
import base64
import uuid
from botocore.exceptions import NoCredentialsError

s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('movies-table-team3')


def upload_movie(event, context):
    try:
        event = json.loads(event["body"])
        id = str(uuid.uuid4())
        file_name = event['file_name']
        file_content_base64 = event['file_content']
        metadata = event['metadata']
        key = f"{id}_{file_name}.mp4"

        file_content = base64.b64decode(file_content_base64)

        bucket = 'movies-team3'
        s3.put_object(Bucket=bucket, Key=key, Body=file_content)

        file_metadata = s3.head_object(Bucket=bucket, Key=key)
        file_type = file_metadata['ContentType']
        file_size = file_metadata['ContentLength']
        last_modified = file_metadata['LastModified'].isoformat()

        item = {
            'id': key,
            'file_type': file_type,
            'file_size': file_size,
            'last_modified': last_modified,
            'title': metadata.get('title', ''),
            'description': metadata.get('description', ''),
            'actors': metadata.get('actors', []),
            'directors': metadata.get('directors', []),
            'genres': metadata.get('genres', []),
            'year': metadata.get('year', '')
        }

        table.put_item(Item=item)

        return {
            'statusCode': 200,
            'body': json.dumps('File uploaded and metadata saved successfully')
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