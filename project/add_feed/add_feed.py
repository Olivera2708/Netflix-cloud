from decimal import Decimal
import json
import boto3
import os

state_machine_arn = os.environ['STATE_MACHINE_ARN']
user_table = os.environ['USER_TABLE']

stepfunctions_client = boto3.client('stepfunctions')
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(user_table)

def custom_serializer(obj):
    if isinstance(obj, Decimal):
        return int(obj)
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

def convert_dynamodb_to_json(data):
    if isinstance(data, dict):
        if 'M' in data:
            return {key: convert_dynamodb_to_json(value) for key, value in data['M'].items()}
        elif 'L' in data:
            return [convert_dynamodb_to_json(item) for item in data['L']]
        elif 'NULL' in data:
            return None
        elif 'BOOL' in data:
            return data['BOOL']
        elif 'S' in data:
            return data['S']
        elif 'N' in data:
            return int(data['N']) if data['N'].isdigit() else float(data['N'])
        else:
            return data
    else:
        return data

def add_feed(event, context):
    for record in event['Records']:
        if record['eventName'] == 'INSERT' or record['eventName'] == 'MODIFY':
            response = table.scan()
            new_image = record['dynamodb']['NewImage']
            new_image = {key: convert_dynamodb_to_json(value) for key, value in new_image.items()}
            for item in response["Items"]:
                combined_input = {
                    'downloaded_genres': item['downloaded_genres'],
                    'user_id': item['id'],
                    'subscriptions': item['subscriptions'],
                    'ratings': item.get('ratings', []),
                    'actors': new_image['actors'],
                    'genres': new_image['genres'],
                    'directors': new_image['directors'],
                    'id': new_image['id'],
                }
                stepfunctions_client.start_execution(
                    stateMachineArn=state_machine_arn,
                    input=json.dumps(combined_input, default=custom_serializer)
                )

    return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
            },
            'body': json.dumps("Success")
        }
