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

def add_feed(event, context):
    try:
        for record in event['Records']:
            if record['eventName'] == 'INSERT':
                response = user_table.scan()
                new_image = record['dynamodb']['NewImage']

                movie_id = new_image['movie_id']['S']
                genres_response = genres_table.query(
                    IndexName='MovieIndex',
                    KeyConditionExpression='movie_id = :id',
                    ExpressionAttributeValues={':id': movie_id}
                )
                genres = [genre_item['genre'] for genre_item in genres_response.get('Items', [])]

                actors_response = actors_table.query(
                    IndexName='MovieIndex',
                    KeyConditionExpression='movie_id = :id',
                    ExpressionAttributeValues={':id': movie_id}
                )
                actors = [actor_item['actor'] for actor_item in actors_response.get('Items', [])]

                directors_response = directors_table.query(
                    IndexName='MovieIndex',
                    KeyConditionExpression='movie_id = :id',
                    ExpressionAttributeValues={':id': movie_id}
                )
                directors = [director_item['director'] for director_item in directors_response.get('Items', [])]
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
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
            },
            'body': json.dumps(f"Error: {str(e)}")
        }
