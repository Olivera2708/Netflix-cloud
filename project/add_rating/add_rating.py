import json
import boto3
import os
from botocore.exceptions import NoCredentialsError

table_movies_name = os.environ['TABLE_MOVIES']
table_feed_name = os.environ['TABLE_FEED']

dynamodb = boto3.resource('dynamodb')
table_movies = dynamodb.Table(table_movies_name)
table_feed = dynamodb.Table(table_feed_name)

cors_headers = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
}

def add_rating(event, context):
    try:
        event_body = json.loads(event.get('body', '{}'))
        if not event_body:
            return {
                'statusCode': 400,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type',
                    'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,DELETE'
                },
                'body': json.dumps({'error': 'Invalid input: body is required'})
            }
        
        user_id = event_body.get('id')
        movie_id = event_body.get("movie_id")
        numbered_rating = event_body.get("rating")
        suggest = event_body.get("suggest")
        likes = event_body.get("likes")
        genres = event_body.get("genres")

        if not (user_id and movie_id and numbered_rating is not None and suggest is not None and likes is not None and genres):
            return {
                'statusCode': 400,
                'headers': cors_headers,
                'body': json.dumps({'error': 'Missing required fields'})
            }
        
        if numbered_rating < 1 or numbered_rating > 5 or suggest not in ["yes", "no"] or likes == "":
            return {
                'statusCode': 500,
                'headers': cors_headers,
                'body': json.dumps({'error': 'Values are not correct'})
            }

        # Update movie table
        response = table_movies.update_item(
            Key={'id': movie_id},
            UpdateExpression="SET #r = list_append(if_not_exists(#r, :empty_list), :rating)",
            ExpressionAttributeNames={'#r': 'ratings'},
            ExpressionAttributeValues={
                ':rating': [{
                    "id": user_id, 
                    "rating": numbered_rating,
                    "suggest": suggest,
                    "likes": likes
                }],
                ':empty_list': []
            },
            ReturnValues="UPDATED_NEW"
        )

        # Update user table
        response = table_feed.update_item(
            Key={'id': user_id},
            UpdateExpression="SET #r = list_append(if_not_exists(#r, :empty_list), :rating)",
            ExpressionAttributeNames={'#r': 'ratings'},
            ExpressionAttributeValues={
                ':rating': [{
                    "movie": movie_id,
                    "rating": numbered_rating,
                    "genres": genres
                }],
                ':empty_list': []
            },
            ReturnValues="UPDATED_NEW"
        )

        return {
            'statusCode': 200,
            'headers': cors_headers,
            'body': json.dumps({"message": "success"})
        }

    except NoCredentialsError:
        return {
            'statusCode': 403,
            'headers': cors_headers,
            'body': json.dumps({'error': 'Credentials not available'})
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': cors_headers,
            'body': json.dumps(f"An error occurred: {str(e)}")
        }
