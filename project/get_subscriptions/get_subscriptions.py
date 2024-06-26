import json
import boto3
import os
from botocore.exceptions import ClientError

table = os.environ['TABLE_FEED']

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(table)


def get_subscriptions(event, context):
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
        item = response['Item']

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
            'body': json.dumps(str(item['subscriptions'])),
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
