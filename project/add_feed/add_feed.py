import json

def add_feed(event, context):
    message = ""
    message += "Received event: " + json.dumps(event, indent=2)
    for record in event['Records']:
        if record['eventName'] == 'INSERT':
            message += "\nNew item added: ", record['dynamodb']['NewImage']
        elif record['eventName'] == 'MODIFY':
            message += "Item modified: ", record['dynamodb']['NewImage']

    return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
            },
            'body': json.dumps(str(message))
        }
