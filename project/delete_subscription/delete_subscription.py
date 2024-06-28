import json
import boto3
import os
from botocore.exceptions import NoCredentialsError
import logging

LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)
table_feed_name = os.environ['TABLE_FEED']
dynamodb = boto3.resource('dynamodb')
table_feed = dynamodb.Table(table_feed_name)
sns = boto3.client('sns')

cors_headers = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
}


def delete_subscription(event, context):
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
                'body': json.dumps({'error': 'Item not found'})
            }

        item = response['Item']["subscriptions"]
        subscriptions = item.get(update_field, [])
        
        if value_to_update in subscriptions:
            try:
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
                unsubscribe_from_topic(topic_arn, user_id)

                if is_topic_empty(topic_arn):
                    sns.delete_topic(TopicArn=topic_arn)
            except Exception:
                return {
                    'statusCode': 400,
                    'headers': cors_headers,
                    'body': json.dumps({'error': 'Pending subscriptions cannot be unsubscribed'})
                }

            subscriptions.remove(value_to_update)
            table_feed.update_item(
                Key={'id': user_id},
                UpdateExpression=f"SET subscriptions.{update_field} = :updated_list",
                ExpressionAttributeValues={':updated_list': subscriptions}
            )



        return {
            'statusCode': 200,
            'headers': cors_headers,
            'body': json.dumps({'message': 'Subscription deleted successfully'})
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


def create_sns_topic(topic_name):
    response = sns.create_topic(Name=topic_name)
    return response['TopicArn']


def unsubscribe_from_topic(topic_arn, email):
    subscriptions = sns.list_subscriptions_by_topic(TopicArn=topic_arn)['Subscriptions']
    for subscription in subscriptions:
        if subscription['Endpoint'] == email and subscription['Protocol'] == 'email':
            sns.unsubscribe(SubscriptionArn=subscription['SubscriptionArn'])
            break


def is_topic_empty(topic_arn):
    subscriptions = sns.list_subscriptions_by_topic(TopicArn=topic_arn)['Subscriptions']
    return len(subscriptions) == 0
