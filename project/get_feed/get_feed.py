from decimal import Decimal
import json
import boto3
import os

table_feed = os.environ['TABLE_FEED']
movie_table = os.environ['MOVIE_TABLE']
N = os.environ['N']

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

def upload_feed(event, context):
    user_id = event['user_id']

    response = table.get_item(
            Key={'id': user_id}
    )

    films = response['Item']['feed']

    sorted_films = sorted(films.keys(), key=lambda k: films[k]['score'], reverse=True)

    result = []

    for i in range(sorted_films):
        if i > N: break
        film = movie_table.get_item(
            Key={'id': sorted_films[i]}
        )
        result.append(film)

    return {
        'statusCode': 200,
        'body': json.dumps(result),
        'headers': {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
        }
    }