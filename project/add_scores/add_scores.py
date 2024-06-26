import json
import boto3
import os
from botocore.exceptions import ClientError

table_feed = os.environ['TABLE_FEED']
dynamodb = boto3.resource('dynamodb')
table_feed = dynamodb.Table(table_feed)

def add_scores(event, context):
    try:
        # struktura zahteva
        # {
        #     user_id: "gligoric383@gmail.com"
        #     for_update: "subscriptions",
        #     payload: {
        #         command: "add"/"remove",
        #         for_update: "genres",
        #         value: "Drama"
        #     }
        # }
      
      
        # event = json.loads(event['body'])
        # if not event:
        #     return {
        #         'statusCode': 400,
        #         'headers': {
        #             'Access-Control-Allow-Origin': '*',
        #             'Access-Control-Allow-Headers': 'Content-Type',
        #             'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,PUT,DELETE'
        #         },
        #         'body': json.dumps({'error': 'Invalid input: body is required'})
        #     }


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
        # if for_update == "subscriptions":
        response = table_feed.get_item(
            Key={'id': 'mbojanic53+2@gmail.com'}
        )
        current_item = response['Item']
        current_item['feed']['Avenger_Endgame_d64aff03-b1d6-4b95-aa3f-99e019ddc9e3'] = 2
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
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,PUT,DELETE'
            },
            'body': json.dumps(f"An error occurred: {str(response)} \n---------\n")
        }