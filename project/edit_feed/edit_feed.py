from decimal import Decimal
import json
import boto3
import os

state_machine_arn = os.environ['STATE_MACHINE_ARN']
user_table_name = os.environ['USER_TABLE']
movies_table_name = os.environ['MOVIES_TABLE']
genres_table_name = os.environ['GENRES_TABLE']
actors_table_name = os.environ['ACTORS_TABLE']
directors_table_name = os.environ['DIRECTORS_TABLE']

stepfunctions_client = boto3.client('stepfunctions')
dynamodb = boto3.resource('dynamodb')

user_table = dynamodb.Table(user_table_name)
movies_table = dynamodb.Table(movies_table_name)
genres_table = dynamodb.Table(genres_table_name)
actors_table = dynamodb.Table(actors_table_name)
directors_table = dynamodb.Table(directors_table_name)

def custom_serializer(obj):
    if isinstance(obj, Decimal):
        return int(obj)
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

# def convert_dynamodb_to_json(data):
#     if isinstance(data, dict):
#         if 'M' in data:
#             return {key: convert_dynamodb_to_json(value) for key, value in data['M'].items()}
#         elif 'L' in data:
#             return [convert_dynamodb_to_json(item) for item in data['L']]
#         elif 'NULL' in data:
#             return None
#         elif 'BOOL' in data:
#             return data['BOOL']
#         elif 'S' in data:
#             return data['S']
#         elif 'N' in data:
#             return int(data['N']) if data['N'].isdigit() else float(data['N'])
#         else:
#             return data
#     else:
#         return data

def edit_feed(event, context):
    for record in event['Records']:
        if record['eventName'] == 'INSERT':
            response = user_table.scan()
            new_image = record['dynamodb']['NewImage']
            movie_id = new_image['movie_id']['S']

            table_name = record['eventSourceARN'].split('/')[1]
            # new_image = {key: convert_dynamodb_to_json(value) for key, value in new_image.items()}

            if 'actor' in table_name or 'genre' in table_name:
                actors_response = actors_table.query(
                    IndexName='MovieIndex',
                    KeyConditionExpression='movie_id = :id',
                    ExpressionAttributeValues={':id': movie_id}
                )
                actors = [actor_item['actor'] for actor_item in actors_response.get('Items', [])]

            if 'director' in table_name or 'genre' in table_name:
                directors_response = directors_table.query(
                    IndexName='MovieIndex',
                    KeyConditionExpression='movie_id = :id',
                    ExpressionAttributeValues={':id': movie_id}
                )
                directors = [director_item['director'] for director_item in directors_response.get('Items', [])]

            if 'genre' in table_name:
                genres_response = genres_table.query(
                    IndexName='MovieIndex',
                    KeyConditionExpression='movie_id = :id',
                    ExpressionAttributeValues={':id': movie_id}
                )
                genres = [genre_item['genre'] for genre_item in genres_response.get('Items', [])]

                for item in response["Items"]:    
                    combined_input = {
                        'downloaded_genres': item['downloaded_genres'],
                        'user_id': item['id'],
                        'subscriptions': item['subscriptions'],
                        'ratings': item.get('ratings', []),
                        'actors': actors,
                        'genres': genres,
                        'directors': directors,
                        'id': movie_id,
                    }
                    stepfunctions_client.start_execution(
                        stateMachineArn=state_machine_arn,
                        input=json.dumps(combined_input, default=custom_serializer)
                    )

    return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
            },
            'body': json.dumps("Success")
        }
