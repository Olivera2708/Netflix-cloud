import json
import boto3
import base64
import uuid
from botocore.exceptions import NoCredentialsError

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('movies-table-team3')
s3 = boto3.client('s3')

def upload_metadata(event, context):
    sqs = boto3.client('sqs')
    
    for record in event['Records']:
        message_body = record['body']
        print(f"Received message: {message_body}")
        process_message(message_body)
        
        # # Delete the message from the queue if necessary
        # receipt_handle = record['receiptHandle']
        # queue_url = 'https://sqs.<region>.amazonaws.com/<account-id>/<queue-name>'
        # sqs.delete_message(
        #     QueueUrl=queue_url,
        #     ReceiptHandle=receipt_handle
        # )

def process_message(event):
    try:
        s3_key = event["key"]
        s3_bucket = event["bucket"]

        response = s3.get_object(Bucket=s3_bucket, Key=s3_key)
        json_data = response['Body'].read().decode('utf-8')
        data = json.loads(json_data)

        bucket = 'movies-team3'
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