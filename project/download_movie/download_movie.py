import json
import boto3
from botocore.exceptions import ClientError

s3_client = boto3.client('s3')

def lambda_handler(event, context):
    bucket_name = event['queryStringParameters']['bucket']
    object_key = event['queryStringParameters']['key']
    
    try:
        response = s3_client.generate_presigned_url('get_object',
                                                    Params={'Bucket': bucket_name, 'Key': object_key},
                                                    ExpiresIn=3600)
        
        return {
            'statusCode': 200,
            'body': json.dumps({'url': response}),
            'headers': {
                'Content-Type': 'application/json'
            }
        }
    except ClientError as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)}),
            'headers': {
                'Content-Type': 'application/json'
            }
        }
