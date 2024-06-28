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

def convert_dynamodb_to_json(data):
    if isinstance(data, dict):
        if 'M' in data:
            return {key: convert_dynamodb_to_json(value) for key, value in data['M'].items()}
        elif 'L' in data:
            return [convert_dynamodb_to_json(item) for item in data['L']]
        elif 'NULL' in data:
            return None
        elif 'BOOL' in data:
            return data['BOOL']
        elif 'S' in data:
            return data['S']
        elif 'N' in data:
            return int(data['N']) if data['N'].isdigit() else float(data['N'])
        else:
            return data
    else:
        return data

def get_feed(event, context):
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