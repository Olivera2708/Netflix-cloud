import json
import boto3
import os
from botocore.exceptions import NoCredentialsError

bucket = os.environ['BUCKET']
table = os.environ['TABLE']

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(table)
s3 = boto3.client('s3')

def upload_metadata(event, context):
    for record in event['Records']:
        try:
            message_body = record['body']
            data = json.loads(message_body)
            if not data:
                raise ValueError('Invalid input: body is required')

            process_message(message_body)

        except Exception as e:
            raise e

def process_message(event):
    try:
        event = json.loads(event)
        s3_key = event["key"]
        s3_bucket = event["bucket"]

        response = s3.get_object(Bucket=s3_bucket, Key=s3_key)
        json_data = response['Body'].read().decode('utf-8')
        data = json.loads(json_data)

        key = data["id"]
        file_metadata = s3.head_object(Bucket=bucket, Key=key)
        
        file_type = file_metadata['ContentType']
        file_size = file_metadata['ContentLength']
        last_modified = file_metadata['LastModified'].isoformat()

        data = data["metadata"]

        item = {
            'id': key,
            'file_type': file_type,
            'file_size': file_size,
            'last_modified': last_modified,
            'title': data.get('title', ''),
            'description': data.get('description', ''),
            'actors': data.get('actors', []),
            'directors': data.get('directors', []),
            'genres': data.get('genres', []),
            'year': data.get('year', '')
        }

        table.put_item(Item=item)
        s3.delete_object(Bucket=s3_bucket, Key=s3_key)

        return {
            'statusCode': 200,
            'body': json.dumps('Metadata saved successfully')
        }
    except Exception as e:
        raise e