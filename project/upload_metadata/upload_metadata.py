import json
import boto3
import os
import uuid
from botocore.exceptions import NoCredentialsError

bucket = os.environ['BUCKET']
movies_table_name = os.environ['MOVIES_TABLE']
genres_table_name = os.environ['GENRES_TABLE']
actors_table_name = os.environ['ACTORS_TABLE']
directors_table_name = os.environ['DIRECTORS_TABLE']
search_table_name = os.environ['SEARCH_TABLE']

dynamodb = boto3.resource('dynamodb')
movies_table = dynamodb.Table(movies_table_name)
genres_table = dynamodb.Table(genres_table_name)
actors_table = dynamodb.Table(actors_table_name)
directors_table = dynamodb.Table(directors_table_name)
search_table = dynamodb.Table(search_table_name)
s3 = boto3.client('s3')

def upload_metadata(event, context):
    for record in event['Records']:
        try:
            message_body = record['body']
            data = json.loads(message_body)
            if not data:
                raise ValueError('Invalid input: body is required')
            process_message(data[0])

        except Exception as e:
            raise e

def process_message(event):
    try:
        s3_key = event["key"]
        s3_bucket = event["bucket"]

        response = s3.get_object(Bucket=s3_bucket, Key=s3_key)
        json_data = response['Body'].read().decode('utf-8')
        data = json.loads(json_data)

        key = f"{data['id']}original.mp4"
        table_key = data['id'][:-1]
        file_metadata = s3.head_object(Bucket=bucket, Key=key)
        
        file_type = file_metadata['ContentType']
        file_size = file_metadata['ContentLength']
        last_modified = file_metadata['LastModified'].isoformat()

        data = data["metadata"]

        item = {
            'id': table_key,
            'file_type': file_type,
            'file_size': file_size,
            'last_modified': last_modified,
            'title': data.get('title', ''),
            'description': data.get('description', ''),
            'year': data.get('year', '')
        }

        # Insert into genres table
        for genre in data.get('genres', []):
            genres_table.put_item(Item={
                'movie_id': table_key,
                'genre': genre,
                'id': str(uuid.uuid4())
            })

        # Insert into actors table
        for actor in data.get('actors', []):
            actors_table.put_item(Item={
                'movie_id': table_key,
                'actor': actor,
                'id': str(uuid.uuid4())
            })

        # Insert into directors table
        for director in data.get('directors', []):
            directors_table.put_item(Item={
                'movie_id': table_key,
                'director': director,
                'id': str(uuid.uuid4())
            })

        add_to_search_table(data, table_key)

        movies_table.put_item(Item=item)
        s3.delete_object(Bucket=s3_bucket, Key=s3_key)
        return {
            'statusCode': 200,
            'body': json.dumps('Metadata saved successfully')
        }
    except Exception as e:
        raise e


def add_to_search_table(data, movie_id):
    title = data.get("title")
    description = data.get("description")
    actors = data.get("actors")
    directors = data.get("directors")
    genres = data.get("genres")
    string_actors = ",".join(actors)
    string_directors = ",".join(directors)
    string_genres = ",".join(genres)
    search = f"{title}_{description}_{string_actors}_{string_directors}_{string_genres}"

    search_table.put_item(Item={
        'movie_id': movie_id,
        'search': search
    })
