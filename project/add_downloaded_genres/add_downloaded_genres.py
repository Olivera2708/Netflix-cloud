import json
import boto3
import os
from botocore.exceptions import NoCredentialsError

table_feed_name = os.environ['TABLE_FEED']

dynamodb = boto3.resource('dynamodb')
table_feed = dynamodb.Table(table_feed_name)

cors_headers = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
}

def add_downloaded_genres(event, context):
    try:
        event_body = json.loads(event.get('body', '{}'))
        if not event_body:
            return {
                'statusCode': 400,
                'headers': cors_headers,
                'body': json.dumps({'error': 'Invalid input: body is required'})
            }
        
        user_id = event_body.get('id')
        genres = event_body.get("genres")

        if not user_id or not genres:
            return {
                'statusCode': 400,
                'headers': cors_headers,
                'body': json.dumps({'error': 'Missing required fields'})
            }
        
        if genres == []:
            return {
                'statusCode': 200,
                'headers': cors_headers,
                'body': json.dumps({"message": "success"})
            }

        table_feed.update_item(
            Key={'id': user_id},
            UpdateExpression="SET #dg = list_append(if_not_exists(#dg, :empty_list), :new_genre_list)",
            ExpressionAttributeNames={'#dg': 'downloaded_genres'},
            ExpressionAttributeValues={
                ':new_genre_list': [genres],
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
