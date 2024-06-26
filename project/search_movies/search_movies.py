import json
import boto3
import os
from boto3.dynamodb.conditions import Key

movies_table_name = os.environ['MOVIES_TABLE']
genres_table_name = os.environ['GENRES_TABLE']
actors_table_name = os.environ['ACTORS_TABLE']
directors_table_name = os.environ['DIRECTORS_TABLE']

dynamodb = boto3.resource('dynamodb')
movies_table = dynamodb.Table(movies_table_name)
genres_table = dynamodb.Table(genres_table_name)
actors_table = dynamodb.Table(actors_table_name)
directors_table = dynamodb.Table(directors_table_name)


def search_movies(event, context):
    try:
        params = event.get('queryStringParameters', {})
        search_value = params.get('value')
        all_movie_ids = set()
        
        # genres_response = genres_table.query(
        #     IndexName='MovieIndex',
        #     KeyConditionExpression='genre = :id',
        #     ExpressionAttributeValues={':id': movie_id},
        #     ProjectionExpression='genre'
        # )
        genres_response = genres_table.query(
            IndexName='GenreIndex',
            KeyConditionExpression=Key('genre').eq(search_value),
            ProjectionExpression='movie_id'
        )
        # for item in genres_response.get('Items', []):
        #     all_movie_ids.add(item['movie_id'])

        # actors_response = actors_table.query(
        #     IndexName='MovieIndex',
        #     KeyConditionExpression=Key('actor').eq(search_value),
        #     ProjectionExpression='movie_id'
        # )
        # for item in actors_response.get('Items', []):
        #     all_movie_ids.add(item['movie_id'])

        # directors_response = directors_table.query(
        #     IndexName='MovieIndex',
        #     KeyConditionExpression=Key('director').eq(search_value),
        #     ProjectionExpression='movie_id'
        # )
        # for item in directors_response.get('Items', []):
        #     all_movie_ids.add(item['movie_id'])

        # title_response = movie_table.query(
        #     IndexName='TitleIndex',
        #     KeyConditionExpression=Key('title').eq(search_value),
        #     ProjectionExpression='id'
        # )
        # for item in title_response.get('Items', []):
        #     all_movie_ids.add(item['id'])

        # description_response = movie_table.query(
        #     IndexName='DescriptionIndex',
        #     KeyConditionExpression=Key('description').eq(search_value),
        #     ProjectionExpression='id'
        # )
        # for item in description_response.get('Items', []):
        #     all_movie_ids.add(item['id'])

        # keys = [{'id': movie_id} for movie_id in all_movie_ids]
        # movie_details = batch_get_items(keys, {
        #     movies_table_name: ['id', 'year', 'title', 'description'],
        #     genres_table_name: ['genre'],
        #     actors_table_name: ['actor'],
        #     directors_table_name: ['director']
        # })


        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
            },
            'body': json.dumps(all_movie_ids)
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

# def batch_get_items(keys, table_names):
#     responses = {table: [] for table in table_names}
#     while keys:
#         batch_keys = keys[:100]
#         keys = keys[100:]

#         request_items = {table: {'Keys': batch_keys} for table in table_names}
#         response = dynamodb.batch_get_item(RequestItems=request_items)

#         for table in table_names:
#             responses[table].extend(response['Responses'].get(table, []))
        
#         unprocessed_keys = response.get('UnprocessedKeys', {})

#         while unprocessed_keys:
#             response = dynamodb.batch_get_item(RequestItems=unprocessed_keys)
#             for table in table_names:
#                 responses[table].extend(response['Responses'].get(table, []))
#             unprocessed_keys = response.get('UnprocessedKeys', {})

#     return responses