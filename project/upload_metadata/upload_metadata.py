import json
import boto3
import base64
import uuid
from botocore.exceptions import NoCredentialsError

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('movies-table-team3')


def upload_metadata(event, context):
    try:
        metadata = json.loads(event["body"])
        key = metadata["id"]
        file_metadata = metadata["file_metadata"]
        file_type = file_metadata['ContentType']
        file_size = file_metadata['ContentLength']
        last_modified = file_metadata['LastModified']

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
            'body': json.dumps('Metadata saved successfully')
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