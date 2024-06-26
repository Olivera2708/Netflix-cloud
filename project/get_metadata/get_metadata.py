import json
import boto3
import os
from botocore.exceptions import ClientError

movies_table_name = os.environ['MOVIES_TABLE']
genres_table_name = os.environ['GENRES_TABLE']
actors_table_name = os.environ['ACTORS_TABLE']
directors_table_name = os.environ['DIRECTORS_TABLE']

dynamodb = boto3.resource('dynamodb')
movies_table = dynamodb.Table(movies_table_name)
genres_table = dynamodb.Table(genres_table_name)
actors_table = dynamodb.Table(actors_table_name)
directors_table = dynamodb.Table(directors_table_name)

def get_metadata(event, context):
    params = event.get('queryStringParameters', {})
    movie_id = params.get('id')

    if not movie_id:
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
        response = movies_table.get_item(Key={'id': movie_id})
        movie_item = response.get('Item')

        if not movie_item:
            return {
                'statusCode': 404,
                'body': json.dumps('Movie not found'),
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type',
                    'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
                }
            }

        genres_response = genres_table.query(
            IndexName='MovieIndex',
            KeyConditionExpression='movie_id = :id',
            ExpressionAttributeValues={':id': movie_id},
            ProjectionExpression='genre'
        )
        genres = [genre_item['genre'] for genre_item in genres_response.get('Items', [])]

        actors_response = actors_table.query(
            IndexName='MovieIndex',
            KeyConditionExpression='movie_id = :id',
            ExpressionAttributeValues={':id': movie_id},
            ProjectionExpression='actor'
        )
        actors = [actor_item['actor'] for actor_item in actors_response.get('Items', [])]

        directors_response = directors_table.query(
            IndexName='MovieIndex',
            KeyConditionExpression='movie_id = :id',
            ExpressionAttributeValues={':id': movie_id},
            ProjectionExpression='director'
        )
        directors = [director_item['director'] for director_item in directors_response.get('Items', [])]

        metadata = {
            'title': movie_item.get('title'),
            'description': movie_item.get('description'),
            'genres': genres,
            'actors': actors,
            'year': movie_item.get('year'),
            'directors': directors
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
