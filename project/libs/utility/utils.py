import json

def create_response(status, body):
    return { 
        'statusCode': status, 
        'headers': {
            'Access-Control-Allow-Origin': '*',
        },
        'body': json.dumps(body, default=str)
        }