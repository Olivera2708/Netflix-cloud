import json
import boto3
from botocore.exceptions import NoCredentialsError

s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('movies-table-team3')


def upload_movie(event, context):
    try:
        file_name = event['file_name']
        file_content = event['file_content']
        metadata = event['metadata']

        bucket = 'movies-team3'
        s3.put_object(Bucket=bucket, Key=file_name, Body=file_content)

        file_metadata = s3.head_object(Bucket=bucket, Key=file_name)
        file_type = file_metadata['ContentType']
        file_size = file_metadata['ContentLength']
        creation_time = file_metadata['LastModified'].isoformat()
        last_modified = file_metadata['LastModified'].isoformat()

        item = {
            'file_name': file_name,
            'file_type': file_type,
            'file_size': file_size,
            'creation_time': creation_time,
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