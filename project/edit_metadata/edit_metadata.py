import json
import boto3
import os
from botocore.exceptions import ClientError

table_name = os.environ['TABLE']
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(table_name)

def edit_metadata(event, context):
    try:
        data = json.loads(event["body"])
        item_id = data["id"]
        if not item_id:
            print("No id present in request")
            return {
                'statusCode': 500,
                'body': json.dumps({'message': 'No id present in request'}),
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type',
                    'Access-Control-Allow-Methods': 'OPTIONS,PUT,POST,GET'
                }
            }

        data = data["metadata"]
        update_expression = "SET "
        expression_attribute_values = {}
        expression_attribute_names = {}
        
        for key, value in data.items():
            if key == "year":
                update_expression += "#yr = :year, "
                expression_attribute_names["#yr"] = "year"
                expression_attribute_values[":year"] = value
            else:
                update_expression += f"{key} = :{key}, "
                expression_attribute_values[f":{key}"] = value
        
        update_expression = update_expression.rstrip(", ")

        table.update_item(
            Key={'id': item_id},
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_attribute_values,
            ExpressionAttributeNames=expression_attribute_names if expression_attribute_names else None,
            ReturnValues="UPDATED_NEW"
        )
        
        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Success'}),
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'OPTIONS,PUT,POST,GET'
            }
        }

    except (json.JSONDecodeError, ValueError) as e:
        print(f"JSON decode error: {e}")
        return {
            'statusCode': 400,
            'body': json.dumps({'message': str(e)}),
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'OPTIONS,PUT,POST,GET'
            }
        }

    except ClientError as e:
        print(f"ClientError: {e}")
        return {
            'statusCode': 400,
            'body': json.dumps({'message': 'Error while editing item in DynamoDB', 'error': str(e)}),
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'OPTIONS,PUT,POST,GET'
            }
        }

    except Exception as e:
        print(f"Internal Server Error: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({'message': 'Internal Server Error', 'error': str(e)}),
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'OPTIONS,PUT,POST,GET'
            }
        }
