import os

import boto3
from boto3.dynamodb.conditions import Key
import logging

LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)

table_movies_name = os.environ['TABLE_MOVIES']
table_feed_name = os.environ['TABLE_FEED']
genres_table_name = os.environ['GENRES_TABLE']
actors_table_name = os.environ['ACTORS_TABLE']
directors_table_name = os.environ['DIRECTORS_TABLE']

dynamodb = boto3.resource('dynamodb')
sns = boto3.client('sns')

table_movies = dynamodb.Table(table_movies_name)
table_feed = dynamodb.Table(table_feed_name)
genres_table = dynamodb.Table(genres_table_name)
actors_table = dynamodb.Table(actors_table_name)
directors_table = dynamodb.Table(directors_table_name)


def notify_subscribers(event, context):
    for record in event['Records']:
        if record['eventName'] == 'INSERT':
            new_image = record['dynamodb']['NewImage']
            LOGGER.info('Ovo je nesto: %s', str(record['dynamodb']['NewImage']))

            movie_id = new_image['id']['S']
            actors = get_actors_by_movie_id(movie_id)
            notify_actors_subscribers(movie_id, actors)

            directors = get_directors_by_movie_id(movie_id)
            notify_directors_subscribers(movie_id, directors)

            genres = get_genres_by_movie_id(movie_id)
            notify_genres_subscribers(movie_id, genres)


def get_actors_by_movie_id(movie_id):
    response = actors_table.query(
        IndexName='MovieIndex',  # Ensure this matches the name of the GSI (Global Secondary Index) on movie_id
        KeyConditionExpression=Key('movie_id').eq(movie_id),
        ProjectionExpression='actor'
    )
    actors = response['Items']
    return [actor['actor'] for actor in actors]


def get_directors_by_movie_id(movie_id):
    response = directors_table.query(
        IndexName='MovieIndex',  # Ensure this matches the name of the GSI (Global Secondary Index) on movie_id
        KeyConditionExpression=Key('movie_id').eq(movie_id),
        ProjectionExpression='director'
    )
    directors = response['Items']
    return [director['director'] for director in directors]


def get_genres_by_movie_id(movie_id):
    response = genres_table.query(
        IndexName='MovieIndex',  # Ensure this matches the name of the GSI (Global Secondary Index) on movie_id
        KeyConditionExpression=Key('movie_id').eq(movie_id),
        ProjectionExpression='genre'
    )
    genres = response['Items']
    return [genre['genre'] for genre in genres]


def notify_actors_subscribers(movie_id, actors):
    for actor_name in actors:
        topic_arn = create_sns_topic("actor_" + actor_name.replace(" ", "_"))
        message = f"A new movie with ID {movie_id} featuring {actor_name} has been added."
        subject = f"New Movie Added with {actor_name}"
        publish_to_sns(topic_arn, subject, message)


def notify_directors_subscribers(movie_id, directors):
    for director_name in directors:
        topic_arn = create_sns_topic("director_" + director_name.replace(" ", "_"))
        message = f"A new movie with ID {movie_id} directed by {director_name} has been added."
        subject = f"New Movie Directed by {director_name}"
        publish_to_sns(topic_arn, subject, message)


def notify_genres_subscribers(movie_id, genres):
    for genre_name in genres:
        topic_arn = create_sns_topic("genre_" + genre_name.replace(" ", "_"))
        message = f"A new movie with ID {movie_id} in the {genre_name} genre has been added."
        subject = f"New {genre_name} Movie Added"
        publish_to_sns(topic_arn, subject, message)


def create_sns_topic(topic_name):
    response = sns.create_topic(Name=topic_name)
    return response['TopicArn']


def publish_to_sns(topic_arn, subject, message):
    response = sns.publish(
        TopicArn=topic_arn,
        Message=message,
        Subject=subject
    )
    print(f"Message sent to SNS topic. Message ID: {response['MessageId']}")
