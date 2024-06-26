import json
import boto3
import uuid
import os
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key

movies_table_name = os.environ['MOVIES_TABLE']
genres_table_name = os.environ['GENRES_TABLE']
actors_table_name = os.environ['ACTORS_TABLE']
directors_table_name = os.environ['DIRECTORS_TABLE']

dynamodb = boto3.resource('dynamodb')
movies_table = dynamodb.Table(movies_table_name)
genres_table = dynamodb.Table(genres_table_name)
actors_table = dynamodb.Table(actors_table_name)
directors_table = dynamodb.Table(directors_table_name)

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

        metadata = data.get("metadata", {})

        response = genres_table.query(
            IndexName='MovieIndex',
            KeyConditionExpression=Key('movie_id').eq(item_id)
        )
        for item in response['Items']:
            genres_table.delete_item(
                Key={'id': item['id']}
            )
        for genre in metadata.get('genres', []):
            genres_table.put_item(Item={
                'movie_id': item_id,
                'genre': genre,
                'id': str(uuid.uuid4())
            })

        response = actors_table.query(
            IndexName='MovieIndex',
            KeyConditionExpression=Key('movie_id').eq(item_id)
        )
        for item in response['Items']:
            actors_table.delete_item(
                Key={'id': item['id']}
            )
        for actor in metadata.get('actors', []):
            actors_table.put_item(Item={
                'movie_id': item_id,
                'actor': actor,
                'id': str(uuid.uuid4())
            }) 

        response = directors_table.query(
            IndexName='MovieIndex',
            KeyConditionExpression=Key('movie_id').eq(item_id)
        )
        for item in response['Items']:
            directors_table.delete_item(
                Key={'id': item['id']}
            )
        for director in metadata.get('directors', []):
            directors_table.put_item(Item={
                'movie_id': item_id,
                'director': director,
                'id': str(uuid.uuid4())
            })

        update_expression = "SET "
        expression_attribute_values = {}
        expression_attribute_names = {}
        
        for key, value in metadata.items():
            if key in ["actors", "directors", "genres"]:
                continue
            elif key == "year":
                update_expression += "#yr = :year, "
                expression_attribute_names["#yr"] = "year"
                expression_attribute_values[":year"] = value
            else:
                update_expression += f"{key} = :{key}, "
                expression_attribute_values[f":{key}"] = value
        
        update_expression = update_expression.rstrip(", ")

        movies_table.update_item(
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
