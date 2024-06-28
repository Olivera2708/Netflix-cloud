import os
import boto3
from boto3.dynamodb.conditions import Key

# Environment Variables
table_movies_name = os.environ['TABLE_MOVIES']
table_feed_name = os.environ['TABLE_FEED']
genres_table_name = os.environ['GENRES_TABLE']
actors_table_name = os.environ['ACTORS_TABLE']
directors_table_name = os.environ['DIRECTORS_TABLE']

# Initialize DynamoDB and SNS
dynamodb = boto3.resource('dynamodb')
sns = boto3.client('sns')

# DynamoDB Tables
table_movies = dynamodb.Table(table_movies_name)
table_feed = dynamodb.Table(table_feed_name)
genres_table = dynamodb.Table(genres_table_name)
actors_table = dynamodb.Table(actors_table_name)
directors_table = dynamodb.Table(directors_table_name)

def notify_subscribers(event, context):
    for record in event['Records']:
        if record['eventName'] == 'INSERT':
            new_image = record['dynamodb']['NewImage']
            movie_id = new_image['id']['S']
            title = new_image['title']['S']

            try:
                actors = get_actors_by_movie_id(movie_id)
                notify_actors_subscribers(title, actors)
            except Exception as e:
                print(f"Error notifying actors subscribers: {e}")

            try:
                directors = get_directors_by_movie_id(movie_id)
                notify_directors_subscribers(title, directors)
            except Exception as e:
                print(f"Error notifying directors subscribers: {e}")

            try:
                genres = get_genres_by_movie_id(movie_id)
                notify_genres_subscribers(title, genres)
            except Exception as e:
                print(f"Error notifying genres subscribers: {e}")

def get_actors_by_movie_id(movie_id):
    try:
        response = actors_table.query(
            IndexName='MovieIndex',
            KeyConditionExpression=Key('movie_id').eq(movie_id),
            ProjectionExpression='actor'
        )
        actors = response['Items']
        return [actor['actor'] for actor in actors]
    except Exception as e:
        print(f"Error querying actors: {e}")
        return []

def get_directors_by_movie_id(movie_id):
    try:
        response = directors_table.query(
            IndexName='MovieIndex',
            KeyConditionExpression=Key('movie_id').eq(movie_id),
            ProjectionExpression='director'
        )
        directors = response['Items']
        return [director['director'] for director in directors]
    except Exception as e:
        print(f"Error querying directors: {e}")
        return []

def get_genres_by_movie_id(movie_id):
    try:
        response = genres_table.query(
            IndexName='MovieIndex',
            KeyConditionExpression=Key('movie_id').eq(movie_id),
            ProjectionExpression='genre'
        )
        genres = response['Items']
        return [genre['genre'] for genre in genres]
    except Exception as e:
        print(f"Error querying genres: {e}")
        return []

def notify_actors_subscribers(title, actors):
    for actor_name in actors:
        topic_arn = create_sns_topic("actor_" + actor_name.replace(" ", "_"))
        message = f"A new movie named {title} featuring {actor_name} has been added."
        subject = f"New Movie Added with {actor_name}"
        publish_to_sns(topic_arn, subject, message)

def notify_directors_subscribers(title, directors):
    for director_name in directors:
        topic_arn = create_sns_topic("director_" + director_name.replace(" ", "_"))
        message = f"A new movie named {title} directed by {director_name} has been added."
        subject = f"New Movie Directed by {director_name}"
        publish_to_sns(topic_arn, subject, message)

def notify_genres_subscribers(title, genres):
    for genre_name in genres:
        topic_arn = create_sns_topic("genre_" + genre_name.replace(" ", "_"))
        message = f"A new movie named {title} in the {genre_name} genre has been added."
        subject = f"New {genre_name} Movie Added"
        publish_to_sns(topic_arn, subject, message)

def create_sns_topic(topic_name):
    try:
        response = sns.create_topic(Name=topic_name)
        return response['TopicArn']
    except Exception as e:
        print(f"Error creating SNS topic: {e}")
        return None

def publish_to_sns(topic_arn, subject, message):
    if topic_arn:
        try:
            response = sns.publish(
                TopicArn=topic_arn,
                Message=message,
                Subject=subject
            )
            print(f"Message sent to SNS topic. Message ID: {response['MessageId']}")
        except Exception as e:
            print(f"Error publishing to SNS: {e}")
    else:
        print("Topic ARN is None, message not sent.")
