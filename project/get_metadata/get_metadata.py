import json
import boto3
import os
from botocore.exceptions import ClientError

table = os.environ['TABLE']

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(table)

def get_metadata(event, context):
    params = event.get('queryStringParameters', {})
    id = params.get('id')

    if not id:
        return {
            'statusCode': 400,
            'body': json.dumps('Missing id query parameter'),
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
            }
        }

    try:
        response = table.get_item(Key={'id': id})
        item = response.get('Item')

        metadata = {
            'title': item.get('title'),
            'description': item.get('description'),
            'genres': item.get('genres'),
            'actors': item.get('actors'),
            'year': item.get('year'),
            'directors': item.get('directors')
        }

        if not item:
            return {
                'statusCode': 404,
                'body': json.dumps('Item not found'),
                'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
            }
            }

        return {
            'statusCode': 200,
            'body': json.dumps(metadata),
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
            }
        }

    except ClientError as e:
        return {
            'statusCode': 500,
            'body': json.dumps('Error fetching item from DynamoDB'),
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
            }
        }
