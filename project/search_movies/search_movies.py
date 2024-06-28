import json
import boto3
import os
from boto3.dynamodb.conditions import Key

movies_table_name = os.environ['MOVIES_TABLE']
genres_table_name = os.environ['GENRES_TABLE']
actors_table_name = os.environ['ACTORS_TABLE']
directors_table_name = os.environ['DIRECTORS_TABLE']
search_table_name = os.environ['SEARCH_TABLE']

dynamodb = boto3.resource('dynamodb')
movies_table = dynamodb.Table(movies_table_name)
genres_table = dynamodb.Table(genres_table_name)
actors_table = dynamodb.Table(actors_table_name)
directors_table = dynamodb.Table(directors_table_name)
search_table = dynamodb.Table(search_table_name)

def search_movies(event, context):
    try:
        params = event.get('queryStringParameters', {})
        search_value = params.get('value')
        result = {}
        all_movie_ids = set()

        if search_value.strip() == "":
            response = movies_table.scan(
                ProjectionExpression='id, title, description'
            )
            for item in response.get('Items', []):
                result[item['id']] = item
        elif "_" in search_value:
            search_response = search_table.query(
                IndexName='SearchIndex',
                KeyConditionExpression=Key('search').eq(search_value),
                ProjectionExpression='movie_id'
            )
            for item in search_response.get('Items', []):
                val = item['movie_id']
                id_response = movies_table.query(
                    KeyConditionExpression=Key('id').eq(val),
                    ProjectionExpression='id, title, description'
                )
                for item in id_response.get('Items', []):
                    result[item['id']] = item
        else:
            genres_response = genres_table.query(
                IndexName='GenreIndex',
                KeyConditionExpression=Key('genre').eq(search_value),
                ProjectionExpression='movie_id'
            )
            for item in genres_response.get('Items', []):
                all_movie_ids.add(item['movie_id'])

            actors_response = actors_table.query(
                IndexName='ActorIndex',
                KeyConditionExpression=Key('actor').eq(search_value),
                ProjectionExpression='movie_id'
            )
            for item in actors_response.get('Items', []):
                all_movie_ids.add(item['movie_id'])

            directors_response = directors_table.query(
                IndexName='DirectorIndex',
                KeyConditionExpression=Key('director').eq(search_value),
                ProjectionExpression='movie_id'
            )
            for item in directors_response.get('Items', []):
                all_movie_ids.add(item['movie_id'])

            title_response = movies_table.query(
                IndexName='TitleIndex',
                KeyConditionExpression=Key('title').eq(search_value),
                ProjectionExpression='id, title, description'
            )
            for item in title_response.get('Items', []):
                result[item['id']] = item

            description_response = movies_table.query(
                IndexName='DescriptionIndex',
                KeyConditionExpression=Key('description').eq(search_value),
                ProjectionExpression='id, title, description'
            )
            for item in description_response.get('Items', []):
                result[item['id']] = item

            for val in all_movie_ids:
                id_response = movies_table.query(
                    KeyConditionExpression=Key('id').eq(val),
                    ProjectionExpression='id, title, description'
                )
                for item in id_response.get('Items', []):
                    result[item['id']] = item

        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
            },
            'body': json.dumps(result)
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
            },
            'body': json.dumps(f"An error occurred: {str(e)}")
        }
