import json
import boto3
import uuid
import os

s3 = boto3.client('s3')
state_machine_arn = os.environ['STATE_MACHINE_ARN']
bucket_name = os.environ['BUCKET']

def upload(event, context):
    stepfunctions_client = boto3.client('stepfunctions')

    try:
        input_data = json.loads(event["body"])
        if not input_data:
            return {
                'statusCode': 400,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type',
                    'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
                },
                'body': json.dumps({'error': 'Invalid input: body is required'})
            }

        unique_id = input_data.get("id", "")
        if unique_id == "":
            unique_id = str(uuid.uuid4())
            input_data["id"] = f"{input_data['metadata']['title']}_{unique_id}/".replace(" ", "_")
        else:
            input_data["id"] = f"{unique_id}/"

        #validation
        for field in ['file_content', 'metadata']:
            value = input_data[field]
            if value is None or value == '':
                return {
                    'statusCode': 500,
                    'headers': {
                        'Access-Control-Allow-Origin': '*',
                        'Access-Control-Allow-Headers': 'Content-Type',
                        'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
                    },
                    'body': json.dumps({'error': 'Data is missing'})
                }
            
        metadata = input_data['metadata']
        for field in ['title', 'description', 'actors', 'directors', 'year', 'genres']:
            value = metadata[field]
            if value is None or isinstance(value, (str, list)) and not value:
                return {
                    'statusCode': 500,
                    'headers': {
                        'Access-Control-Allow-Origin': '*',
                        'Access-Control-Allow-Headers': 'Content-Type',
                        'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
                    },
                    'body': json.dumps({'error': 'Data is missing'})
                }

        json_data = json.dumps(input_data)
        s3_key = f'input_data/{unique_id}.json'
        s3.put_object(Bucket=bucket_name, Key=s3_key, Body=json_data)

        s3_reference = {
            "bucket": bucket_name,
            "key": s3_key
        }

        stepfunctions_client.start_execution(
            stateMachineArn=state_machine_arn,
            input=json.dumps(s3_reference)
        )

        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
            },
            'body': json.dumps({'message': 'Success'})
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
            },
            'body': json.dumps({'error': str(e)})
        }