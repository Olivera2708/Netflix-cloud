import json
import boto3
import os
from botocore.exceptions import NoCredentialsError

table_movies = os.environ['TABLE_MOVIES']
table_feed = os.environ['TABLE_FEED']

dynamodb = boto3.resource('dynamodb')
table_movies = dynamodb.Table(table_movies)
table_feed = dynamodb.Table(table_feed)

def upload_user(event, context):
    try:
        event = json.loads(event['body'])
        if not event:
            return {
                'statusCode': 400,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type',
                    'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
                },
                'body': json.dumps({'error': 'Invalid input: body is required'})
            }
        user_id = event['id']
        response = table_movies.scan(ProjectionExpression='id')
        data = response['Items']

        while 'LastEvaluatedKey' in response:
            response = table_movies.scan(
                ProjectionExpression='id',
                ExclusiveStartKey=response['LastEvaluatedKey']
            )
            data.extend(response['Items'])
        feed = {}
        for item in data:
            feed[item['id']] = {
                'score': 0,
                'subscription_score': 0,
                'rating_score': 0,
                'download_score': 0,
            }

        item = {
            'id': user_id,
            'subscriptions': {
                'genres': [],
                'actors': [],
                'directors': []
            },
            'feed': feed,
            'ratings': [],
            'downloaded_genres': []
        }

        table_feed.put_item(Item=item)
        
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
            },
            'body': json.dumps(str(item))
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


