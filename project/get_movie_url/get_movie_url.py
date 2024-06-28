import json
import os
import boto3
from botocore.exceptions import ClientError

s3_client = boto3.client('s3')
bucket = os.environ['BUCKET']

def get_movie_url(event, context):
    object_key = event.get('queryStringParameters', {}).get('key')
    
    try:
        response = s3_client.generate_presigned_url('get_object',
                                                    Params={'Bucket': bucket, 'Key': object_key},
                                                    ExpiresIn=3600)
        
        return {
            'statusCode': 200,
            'body': json.dumps({'url': response}),
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
            }
        }
    except ClientError as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)}),
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
            },
        }
 