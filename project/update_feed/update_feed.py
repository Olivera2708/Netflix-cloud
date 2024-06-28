from decimal import Decimal
import json
import boto3
import os

user_table_name = os.environ['USER_TABLE']
movies_table_name = os.environ['MOVIES_TABLE']
genres_table_name = os.environ['GENRES_TABLE']
actors_table_name = os.environ['ACTORS_TABLE']
directors_table_name = os.environ['DIRECTORS_TABLE']

dynamodb = boto3.resource('dynamodb')

user_table = dynamodb.Table(user_table_name)
movies_table = dynamodb.Table(movies_table_name)
genres_table = dynamodb.Table(genres_table_name)
actors_table = dynamodb.Table(actors_table_name)
directors_table = dynamodb.Table(directors_table_name)

def convert_dynamodb_to_json(data):
    if isinstance(data, dict):
        if 'M' in data:
            return {key: convert_dynamodb_to_json(value) for key, value in data['M'].items()}
        elif 'L' in data:
            return [convert_dynamodb_to_json(item) for item in data['L']]
        elif 'NULL' in data:
            return None
        elif 'BOOL' in data:
            return data['BOOL']
        elif 'S' in data:
            return data['S']
        elif 'N' in data:
            return int(data['N']) if data['N'].isdigit() else float(data['N'])
        else:
            return data
    else:
        return data

def get_movie_genres(movie_id):
    genres_response = genres_table.query(   
        IndexName='MovieIndex',
        KeyConditionExpression='movie_id = :id',
        ExpressionAttributeValues={':id': movie_id}
    )
    return set([genre_item['genre'] for genre_item in genres_response.get('Items', [])])
    
def get_movie_actors(movie_id):
    actors_response = actors_table.query(
        IndexName='MovieIndex',
        KeyConditionExpression='movie_id = :id',
        ExpressionAttributeValues={':id': movie_id}
    )
    return set([actor_item['actor'] for actor_item in actors_response.get('Items', [])])

def get_movie_directors(movie_id):
    directors_response = directors_table.query(
        IndexName='MovieIndex',
        KeyConditionExpression='movie_id = :id',
        ExpressionAttributeValues={':id': movie_id}
    )
    return [director_item['director'] for director_item in directors_response.get('Items', [])]

def update_feed(event, context):
    try:
        for record in event['Records']:
            if record['eventName'] == 'MODIFY':
                new_image = record['dynamodb']['NewImage']
                old_image = record['dynamodb']['OldImage']
                new_image = {key: convert_dynamodb_to_json(value) for key, value in new_image.items()}
                old_image = {key: convert_dynamodb_to_json(value) for key, value in old_image.items()}

                user_id = record['dynamodb']['Keys']['id']['S']
                response = user_table.get_item(
                    Key={'id': user_id}
                )
                current_item = response['Item']
                
                new_downloaded_genres = new_image['downloaded_genres']
                new_subscriptions = new_image['subscriptions']
                new_ratings = new_image['ratings']
                
                old_downloaded_genres = old_image['downloaded_genres']
                old_subscriptions = old_image['subscriptions']
                old_ratings = old_image['ratings']

                if len(new_downloaded_genres) > len(old_downloaded_genres):
                    #preuzeo je
                    diff_downloaded_genre = set(new_downloaded_genres[-1])
                    for movie in new_image['feed']:
                        film_genres = get_movie_genres(movie)
                        current_item['feed'][movie]['download_score'] = Decimal(new_image['feed'][movie]['download_score']/2 + len(diff_downloaded_genre & film_genres) * 3)
                        current_item['feed'][movie]['score'] = current_item['feed'][movie]['download_score'] + current_item['feed'][movie]['rating_score'] + current_item['feed'][movie]['subscription_score']
                    user_table.put_item(Item=current_item)
                elif len(new_ratings) > len(old_ratings):
                    #ocenio je
                    rating_genres = set(new_ratings[-1]['genres'])
                    for movie in new_image['feed']:
                        film_genres = get_movie_genres(movie)
                        current_item['feed'][movie]['rating_score'] = current_item['feed'][movie]['rating_score'] + Decimal(len(rating_genres & film_genres) * new_ratings[-1]['rating'])
                        current_item['feed'][movie]['score'] = current_item['feed'][movie]['download_score'] + current_item['feed'][movie]['rating_score'] + current_item['feed'][movie]['subscription_score']
                    user_table.put_item(Item=current_item)
                elif len(new_subscriptions['actors']) > len(old_subscriptions['actors']):
                    #pretplatio se
                    new_actor = list(set(new_subscriptions['actors']) - set(old_subscriptions['actors']))
                    for movie in new_image['feed']:
                        film_actors = get_movie_actors(movie)
                        current_item['feed'][movie]['subscription_score'] = current_item['feed'][movie]['subscription_score'] + (10 if new_actor[0] in film_actors else 0)
                        current_item['feed'][movie]['score'] = current_item['feed'][movie]['download_score'] + current_item['feed'][movie]['rating_score'] + current_item['feed'][movie]['subscription_score']
                    user_table.put_item(Item=current_item)
                elif  len(new_subscriptions['directors']) > len(old_subscriptions['directors']):
                    new_director = list(set(new_subscriptions['directors']) - set(old_subscriptions['directors']))
                    for movie in new_image['feed']:
                        film_directors = get_movie_directors(movie)
                        current_item['feed'][movie]['subscription_score'] = current_item['feed'][movie]['subscription_score'] + (10 if new_director[0] in film_directors else 0)
                        current_item['feed'][movie]['score'] = current_item['feed'][movie]['download_score'] + current_item['feed'][movie]['rating_score'] + current_item['feed'][movie]['subscription_score']
                    user_table.put_item(Item=current_item)
                elif  len(new_subscriptions['genres']) > len(old_subscriptions['genres']):
                    new_genre = list(set(new_subscriptions['genres']) - set(old_subscriptions['genres']))
                    for movie in new_image['feed']:
                        film_genres = get_movie_genres(movie)
                        current_item['feed'][movie]['subscription_score'] = current_item['feed'][movie]['subscription_score'] + (10 if new_genre[0] in film_genres else 0)
                        current_item['feed'][movie]['score'] = current_item['feed'][movie]['download_score'] + current_item['feed'][movie]['rating_score'] + current_item['feed'][movie]['subscription_score']
                    user_table.put_item(Item=current_item)
                elif len(new_subscriptions['actors']) < len(old_subscriptions['actors']):
                    #obrisao pretplatu
                    deleted_actor = list(set(old_subscriptions['actors']) - set(new_subscriptions['actors']))
                    print(deleted_actor)
                    for movie in new_image['feed']: 
                        film_actors = get_movie_actors(movie)
                        current_item['feed'][movie]['subscription_score'] = current_item['feed'][movie]['subscription_score'] - (10 if deleted_actor[0] in film_actors else 0)
                        current_item['feed'][movie]['score'] = current_item['feed'][movie]['download_score'] + current_item['feed'][movie]['rating_score'] + current_item['feed'][movie]['subscription_score']
                    user_table.put_item(Item=current_item)
                elif  len(new_subscriptions['directors']) < len(old_subscriptions['directors']):
                    deleted_director = list(set(old_subscriptions['directors']) - set(new_subscriptions['directors']))
                    for movie in new_image['feed']:
                        film_directors = get_movie_directors(movie)
                        current_item['feed'][movie]['subscription_score'] = current_item['feed'][movie]['subscription_score'] - (10 if deleted_director[0] in film_directors else 0)
                        current_item['feed'][movie]['score'] = current_item['feed'][movie]['download_score'] + current_item['feed'][movie]['rating_score'] + current_item['feed'][movie]['subscription_score']
                    user_table.put_item(Item=current_item)
                elif  len(new_subscriptions['genres']) < len(old_subscriptions['genres']):
                    deleted_genre = list(set(old_subscriptions['genres']) - set(new_subscriptions['genres']))
                    for movie in new_image['feed']:
                        film_genres = get_movie_genres(movie)
                        current_item['feed'][movie]['subscription_score'] = current_item['feed'][movie]['subscription_score'] - (10 if deleted_genre[0] in film_genres else 0)
                        current_item['feed'][movie]['score'] = current_item['feed'][movie]['download_score'] + current_item['feed'][movie]['rating_score'] + current_item['feed'][movie]['subscription_score']
                    user_table.put_item(Item=current_item)
        return {
                'statusCode': 200,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type',
                    'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
                },
                'body': json.dumps("Success")
            }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
            },
            'body': json.dumps(f"Error: {str(e)}")
        }
