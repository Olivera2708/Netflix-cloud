import json
import os
import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
from boto3.dynamodb.conditions import Key

s3_client = boto3.client('s3')
bucket = os.environ['BUCKET']
feed_table_name = os.environ['FEED_TABLE']
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
feed_table = dynamodb.Table(feed_table_name)

def delete_data(event, context):
    try:
        object_key = event['pathParameters']['id']
        
        if not object_key:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Object key is required'}),
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type',
                    'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,DELETE'
                }
            }
        
        movies_table.delete_item(
            Key={'id': object_key}
        )

        response = genres_table.query(
            IndexName='MovieIndex',
            KeyConditionExpression=Key('movie_id').eq(object_key)
        )
        for item in response['Items']:
            genres_table.delete_item(
                Key={'id': item['id']}
            )

        response = actors_table.query(
            IndexName='MovieIndex',
            KeyConditionExpression=Key('movie_id').eq(object_key)
        )
        for item in response['Items']:
            actors_table.delete_item(
                Key={'id': item['id']}
            )

        response = directors_table.query(
            IndexName='MovieIndex',
            KeyConditionExpression=Key('movie_id').eq(object_key)
        )
        for item in response['Items']:
            directors_table.delete_item(
                Key={'id': item['id']}
            )

        search_table.delete_item(
            Key={'movie_id': object_key}
        )

        remove_from_all_users(object_key)

        s3_objects = s3_client.list_objects_v2(Bucket=bucket, Prefix=object_key)
        if 'Contents' in s3_objects:
            for obj in s3_objects['Contents']:
                s3_client.delete_object(Bucket=bucket, Key=obj['Key'])
        
        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Movie deleted successfully'}),
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,DELETE'
            }
        }
    except (NoCredentialsError, PartialCredentialsError):
        return {
            'statusCode': 401,
            'body': json.dumps({'error': 'Credentials not available'}),
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,DELETE'
            }
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)}),
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,DELETE'
            }
        }

def remove_from_all_users(movie_id):
    response = feed_table.scan()
    for item in response['Items']:
        feed = item['feed']
        updated_feed = {key: value for key, value in feed.items() if key != movie_id}

        feed_table.update_item(
            Key={'id': item['id']},
            UpdateExpression='SET feed = :val',
            ExpressionAttributeValues={':val': updated_feed}
        )
