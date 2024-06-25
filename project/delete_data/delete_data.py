import json
import os
import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError

s3_client = boto3.client('s3')
dynamo_client = boto3.client('dynamodb')
table = os.environ['TABLE']
bucket = os.environ['BUCKET']

def delete_data(event, context):
    try:
        object_key = event['pathParameters']['id']
        
        if not object_key:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Object key is required'}),
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type',
                    'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,DELETE'
                }
            }
        
        dynamo_key = {'id': {'S': object_key}}
        dynamo_client.delete_item(TableName=table, Key=dynamo_key)

        s3_objects = s3_client.list_objects_v2(Bucket=bucket, Prefix=object_key)
        if 'Contents' in s3_objects:
            for obj in s3_objects['Contents']:
                s3_client.delete_object(Bucket=bucket, Key=obj['Key'])
        
        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Movie deleted successfully'}),
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,DELETE'
            }
        }
    except (NoCredentialsError, PartialCredentialsError):
        return {
            'statusCode': 401,
            'body': json.dumps({'error': 'Credentials not available'}),
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,DELETE'
            }
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)}),
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,DELETE'
            }
        }
