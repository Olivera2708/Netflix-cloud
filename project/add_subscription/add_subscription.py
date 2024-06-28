import json
import boto3
import os
from botocore.exceptions import NoCredentialsError, ClientError

table_feed_name = os.environ['TABLE_FEED']
dynamodb = boto3.resource('dynamodb')
table_feed = dynamodb.Table(table_feed_name)
sns = boto3.client('sns')

cors_headers = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,PUT,DELETE'
}


def add_subscription(event, context):
    try:
        event_body = json.loads(event['body'])
        
        if not event_body:
            return {
                'statusCode': 400,
                'headers': cors_headers,
                'body': json.dumps({'error': 'Invalid input: body is required'})
            }
        
        user_id = event_body.get('user_id')
        payload = event_body.get('payload')
        
        if not user_id or not payload:
            return {
                'statusCode': 400,
                'headers': cors_headers,
                'body': json.dumps({'error': 'Invalid input: user_id and payload are required'})
            }
        
        update_field = payload.get('for_update')
        value_to_update = payload.get('value')
        
        if not update_field or not value_to_update:
            return {
                'statusCode': 400,
                'headers': cors_headers,
                'body': json.dumps({'error': 'Invalid input: for_update and value are required in payload'})
            }

        response = table_feed.get_item(Key={'id': user_id})
        if 'Item' not in response:
            return {
                'statusCode': 404,
                'headers': cors_headers,
                'body': json.dumps({'error': 'User not found'})
            }
        if update_field in response['Item']["subscriptions"] and value_to_update in response['Item']["subscriptions"][update_field]:
            return {
                'statusCode': 200,
                'headers': cors_headers,
                'body': json.dumps({"message": "Value already exists"})
            }

        topic_name_prefix = {
            'actors': 'actor_',
            'directors': 'director_',
            'genres': 'genre_'
        }.get(update_field, '')

        if not topic_name_prefix:
            return {
                'statusCode': 400,
                'headers': cors_headers,
                'body': json.dumps({'error': 'Invalid update field'})
            }

        topic_name = topic_name_prefix + value_to_update.replace(" ", "_")
        topic_arn = create_sns_topic(topic_name)
        subscribe_to_topic(topic_arn, user_id)

        response = table_feed.update_item(
            Key={'id': user_id},
            UpdateExpression=f"SET subscriptions.#field = list_append(subscriptions.#field, :value)",
            ExpressionAttributeNames={'#field': update_field},
            ExpressionAttributeValues={':value': [value_to_update]},
            ReturnValues="ALL_NEW"
        )
        
        updated_item = response['Attributes']
        return {
            'statusCode': 200,
            'headers': cors_headers,
            'body': json.dumps({"message": "success"})
        }
    except (NoCredentialsError, ClientError) as e:
        return {
            'statusCode': 500,
            'headers': cors_headers,
            'body': json.dumps(f"An error occurred with AWS: {str(e)}")
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': cors_headers,
            'body': json.dumps(f"An error occurred: {str(e)}")
        }


def create_sns_topic(topic_name):
    response = sns.create_topic(Name=topic_name)
    return response['TopicArn']


def subscribe_to_topic(topic_arn, email):
    sns.subscribe(
        TopicArn=topic_arn,
        Protocol='email',
        Endpoint=email
    )
