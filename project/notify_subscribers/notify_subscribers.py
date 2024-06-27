import json
import boto3
import os
from botocore.exceptions import ClientError

table_movies_name = os.environ['TABLE_MOVIES']
table_feed_name = os.environ['TABLE_FEED']

dynamodb = boto3.resource('dynamodb')
table_movies = dynamodb.Table(table_movies_name)
table_feed = dynamodb.Table(table_feed_name)
sns = boto3.client('sns')


def handler(event, context):
    for record in event['Records']:
        if record['eventName'] == 'INSERT':
            new_image = record['dynamodb']['NewImage']
            movie_id = new_image['movie_id']['S']
            actors = new_image['actors']['L']
            notify_subscribers(movie_id, actors)


def notify_subscribers(movie_id, actors):
    for actor in actors:
        actor_name = actor['S']
        topic_arn = create_sns_topic(actor_name)
        message = f"A new movie with ID {movie_id} featuring {actor_name} has been added."
        subject = f"New Movie Added with {actor_name}"
        publish_to_sns(topic_arn, subject, message)


def create_sns_topic(actor_name):
    response = sns.create_topic(Name=f"actor_{actor_name}")
    return response['TopicArn']


def publish_to_sns(topic_arn, subject, message):
    response = sns.publish(
        TopicArn=topic_arn,
        Message=message,
        Subject=subject
    )
    print(f"Message sent to SNS topic. Message ID: {response['MessageId']}")