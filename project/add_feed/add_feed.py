import json
import boto3
import os

state_machine_arn = os.environ['STATE_MACHINE_ARN']
user_table = os.environ['USER_TABLE']

stepfunctions_client = boto3.client('stepfunctions')
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(user_table)

def add_feed(event, context):
    message = ""
    # message += "Received event: " + json.dumps(event, indent=2)
    for record in event['Records']:
        if record['eventName'] == 'INSERT' or record['eventName'] == 'MODIFY':
            response = table.scan()
            new_image = record['dynamodb']['NewImage']
            new_image = {k: convert_dynamodb_json(v) for k, v in new_image.items()}
            for item in response["Items"]:
                print(item)
                item = {k: convert_dynamodb_json(v) for k, v in item.items()}
                combined_input = {
                    'item': item,
                    'new_image': new_image
                }
                stepfunctions_client.start_execution(
                    stateMachineArn=state_machine_arn,
                    input=json.dumps(combined_input)
                )

    return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
            },
            'body': json.dumps(str(message))
        }

def convert_dynamodb_json(value):
    if 'S' in value:
        return value['S']
    elif 'N' in value:
        return int(value['N'])
    elif 'BOOL' in value:
        return value['BOOL']
    elif 'M' in value:
        return {k: convert_dynamodb_json(v) for k, v in value['M'].items()}
    elif 'L' in value:
        return [convert_dynamodb_json(v) for v in value['L']]
    elif 'NULL' in value:
        return None
    else:
        raise TypeError("Unknown DynamoDB JSON type: {}".format(value))
        