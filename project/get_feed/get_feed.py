from decimal import Decimal
import json
import boto3
import os
from boto3.dynamodb.conditions import Key

table_feed = os.environ['TABLE_FEED']
movie_table = os.environ['MOVIES_TABLE']

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(table_feed)
movie_table = dynamodb.Table(movie_table)

def get_feed(event, context):
    try:
        params = event.get('queryStringParameters', {})
        user_id = params.get('id')
        N = 3

        if not user_id:
            return {
                'statusCode': 400,
                'body': json.dumps('Missing id query parameter'),
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type',
                    'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
                }
            }

        response = table.get_item(
                Key={'id': user_id}
            )

        if 'Item' not in response:
                return {
                    'statusCode': 404,
                    'body': json.dumps('User not found'),
                    'headers': {
                        'Access-Control-Allow-Origin': '*',
                        'Access-Control-Allow-Headers': 'Content-Type',
                        'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
                    }
                }

        films = response['Item']['feed']
        sorted_films = sorted(films.keys(), key=lambda k: films[k]['score'], reverse=True)
        result = {}

        for i in range(len(sorted_films)):
            if i >= N: break
            id_response = movie_table.query(
                KeyConditionExpression=Key('id').eq(sorted_films[i]),
                ProjectionExpression='id, title, description'
            )
            for item in id_response.get('Items', []):
                result[item['id']] = item

        return {
            'statusCode': 200,
            'body': json.dumps(result),
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
            }
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps(f'Internal server error: {str(e)}'),
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
            }
        }
