import json
import boto3
import uuid

s3 = boto3.client('s3')

def upload(event, context):
    stepfunctions_client = boto3.client('stepfunctions')
    state_machine_arn = 'arn:aws:states:eu-central-1:533267409058:stateMachine:TranscodingAndUploading75F01ED0-7s6GZ5G0m7YE'
    bucket_name = 'movies-team3'

    try:
        input_data = json.loads(event["body"])
        if not input_data:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Invalid input: body is required'})
            }

        unique_id = str(uuid.uuid4())
        input_data["id"] = f"{unique_id}_{input_data['file_name']}.mp4"

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
            'body': json.dumps(s3_reference)
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
