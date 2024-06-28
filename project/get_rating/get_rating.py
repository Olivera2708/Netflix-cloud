import json
import boto3
import os
from botocore.exceptions import ClientError

table = os.environ['TABLE']

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(table)

def get_rating(event, context):
    params = event.get('queryStringParameters', {})
    user_id = params.get('user_id')
    movie_id = params.get('movie_id')

    if not user_id or not movie_id:
        return {
            'statusCode': 400,
            'body': json.dumps('Missing id query parameter'),
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
            }
        }

    try:
        response = table.get_item(Key={'id': movie_id})
        item = response.get('Item')

        if not item:
            return {
                'statusCode': 404,
                'body': json.dumps('Item not found'),
                'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
            }
        }

        ratings = item.get("ratings", [])
        n = 0
        avgRating = 0
        suggestProc = 0
        mostLiked = ""
        likes = {}
        alreadyRated = False
        if ratings != []:
            for rating in ratings:
                n += 1
                avgRating += rating.get("rating")
                suggestProc += 1 if rating.get("suggest") == "yes" else 0
                likes[rating.get("likes")] = likes.get(rating.get("likes"), 0) + 1
                if rating.get("id") == user_id:
                    alreadyRated = True

            avgRating /= n
            suggestProc = suggestProc/n*100
            mostLiked = max(likes, key=likes.get)

        result = {
            'avgRating': round(avgRating, 2),
            'suggestProc': round(suggestProc, 0),
            'mostLiked': mostLiked
        }
        result_str = {key: str(value) for key, value in result.items() if key != 'alreadyRated'}
        result_str["alreadyRated"] = alreadyRated

        return {
            'statusCode': 200,
            'body': json.dumps(result_str),
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
            }
        }

    except ClientError as e:
        return {
            'statusCode': 500,
            'body': json.dumps('Error fetching item from DynamoDB'),
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
            }
        }
