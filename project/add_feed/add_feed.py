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
            stepfunctions_client.start_execution(
                stateMachineArn=state_machine_arn,
                input=json.dumps(response)
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
