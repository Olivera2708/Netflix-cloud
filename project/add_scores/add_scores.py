import json
import boto3
import os
from decimal import Decimal
from botocore.exceptions import ClientError

table_feed = os.environ['TABLE_FEED']
dynamodb = boto3.resource('dynamodb')
table_feed = dynamodb.Table(table_feed)

def add_scores(event, context):
    try:
        rating_score = Decimal(str(event[0]['rating_score']))
        subscription_score = Decimal(str(event[1]['subscription_score']))
        download_score = Decimal(str(event[2]['download_score']))
        user_id = event[0]['user_id']
        movie_id = event[0]['movie_id']

        total_score = rating_score + subscription_score + download_score

        response = table_feed.get_item(
            Key={'id': user_id}
        )
        current_item = response['Item']
        
        if movie_id not in current_item['feed']:
            current_item['feed'][movie_id] = {}

        current_item['feed'][movie_id]['score'] = total_score
        current_item['feed'][movie_id]['download_score'] = download_score
        current_item['feed'][movie_id]['rating_score'] = rating_score
        current_item['feed'][movie_id]['subscription_score'] = subscription_score
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
            'body': json.dumps(f"An error occurred: {str(e)} \n---------\n")
        }