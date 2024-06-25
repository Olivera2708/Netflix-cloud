import json
import boto3
import os
from botocore.exceptions import ClientError

table_feed = os.environ['TABLE_FEED']
dynamodb = boto3.resource('dynamodb')
table_feed = dynamodb.Table(table_feed)

def edit_user(event, context):
    try:
        # struktura zahteva
        # {
        #     user_id: "gligoric383@gmail.com"
        #     for_update: "subscriptions",
        #     payload: {
        #         command: "add",
        #         for_update: "genres",
        #         value: "Drama"
        #     }
        # }
        event = json.loads(event['body'])
        if not event:
            return {
                'statusCode': 400,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type',
                    'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,PUT,DELETE'
                },
                'body': json.dumps({'error': 'Invalid input: body is required'})
            }
        user_id = event['user_id']
        for_update = event['for_update']
        payload = event['payload']

        # struktura user tabele
        # item = {
        #     'id': user_id,
        #     'subscriptions': {
        #         'genres': [],
        #         'actors': [],
        #         'directors': []
        #     },
        #     'feed': feed,
        #     'ratings': []
        # }
        if for_update == "subscriptions":
            response = table_feed.get_item(
                Key={'id': user_id}
            )
            current_item = response['Item']
            update_command = payload['command']
            update_field = payload['for_update']
            value_to_update = payload['value']
            if update_command == "add" and value_to_update not in current_item[for_update][update_field]:
                current_item[for_update][update_field].append(value_to_update)
            elif update_command == "remove":
                current_item[for_update][update_field].remove(value_to_update)
            response = table_feed.put_item(Item=current_item)
            return {
                'statusCode': 200,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type',
                    'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,PUT,DELETE'
                },
                'body': json.dumps(str(current_item))
            }
        elif for_update == "feed":
            pass
        elif for_update == "ratings":
            pass

        return {
            'statusCode': 400,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,PUT,DELETE'
            },
            'body': json.dumps("Not a proper field for updating")
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,PUT,DELETE'
            },
            'body': json.dumps(f"An error occurred: {str(e)}")
        }