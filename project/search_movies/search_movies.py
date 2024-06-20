import json
import boto3
import os
from boto3.dynamodb.conditions import Attr

# Initialize DynamoDB resource
dynamodb = boto3.resource('dynamodb')
table_name = os.environ['TABLE']
table = dynamodb.Table(table_name)


def search_movies(event, context):
    try:

        title = event['queryStringParameters']['title']
        description = event['queryStringParameters']['description']
        actors = event['queryStringParameters']['actors']
        directors = event['queryStringParameters']['directors']
        genres = event['queryStringParameters']['genres']

        filter_expression = Attr('title').contains(title)

        filter_expression = filter_expression & Attr('description').contains(
            description) if filter_expression else Attr('description').contains(description)

        for actor in actors:
            filter_expression = filter_expression & Attr('actors').contains(actor) if filter_expression else Attr(
                'actors').contains(actor)

        for director in directors:
            filter_expression = filter_expression & Attr('directors').contains(
                director) if filter_expression else Attr('directors').contains(director)

        for genre in genres:
            filter_expression = filter_expression & Attr('genres').contains(genre) if filter_expression else Attr(
                'genres').contains(genre)

        response = table.scan(
            FilterExpression=filter_expression
        )

        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'GET,POST,OPTIONS'
            },
            'body': response["Items"]
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'GET,POST,OPTIONS'
            },
            'body': json.dumps(f"An error occurred: {str(e)}")
        }
