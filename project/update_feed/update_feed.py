from decimal import Decimal
import json
import boto3
import os

table_feed = os.environ['TABLE_FEED']

stepfunctions_client = boto3.client('stepfunctions')
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(table_feed)

def custom_serializer(obj):
    if isinstance(obj, Decimal):
        return int(obj)
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

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

def update_subscription_score(new_items, old_items, film_items):
    new_item = set(new_items) - set(old_items)
    return 10 if new_item in film_items else 0


def update_feed(event, context):
    for record in event['Records']:
        if record['eventName'] == 'MODIFY':
            new_image = record['dynamodb']['NewImage']
            old_image = record['dynamodb']['OldImage']
            new_image = {key: convert_dynamodb_to_json(value) for key, value in new_image.items()}
            old_image = {key: convert_dynamodb_to_json(value) for key, value in old_image.items()}

            new_genres = new_image['downloaded_genres']
            new_subscriptions = new_image['subscriptions']
            new_ratings = new_image['ratings']
            # new_feed = new_image['feed']
            
            old_genres = old_image['downloaded_genres']
            old_subscriptions = old_image['subscriptionsv']
            old_ratings = old_image['ratings']

            for film in new_image['feed']:
                if len(new_genres) > len(old_genres):
                    #preuzeo je
                    new_genre = set([item for item in new_genres if item not in old_genres][0])
                    # new_genre = list(set(new_genres) - set(old_genres))
                    #dobavi zanrove filma, DECIMAL
                    film_genres = set(['Action'])
                    new_image['feed'][film]['download_score'] = new_image['feed'][film]['download_score']/2 + len(new_genre & film_genres) * 3
                elif len(new_ratings) > len(old_ratings):
                    #ocenio je
                    new_rating = set([item for item in new_ratings if item not in old_ratings][0])
                    rating_genres = set(new_rating['genres'])
                    #dobavi zanrove filma, DECIMAL 
                    film_genres = set(['Action'])
                    new_image['feed'][film]['rating_score'] += len(rating_genres & film_genres) * new_rating['rating']
                elif len(new_subscriptions['actors']) > len(old_subscriptions['actors']):
                    #pretplatio se
                    # new_actor = set(new_subscriptions['actors']) - set(old_subscriptions['actors'])
                    #dobavi glumce filma, DECIMAL 
                    film_actors = set(['Actor Actor'])
                    # new_image['feed'][film]['subscription_score'] += (10 if new_actor in film_actors else 0)
                    new_image['feed'][film]['subscription_score'] += update_subscription_score(new_subscriptions['actors'], old_subscriptions['actors'], film_actors)
                elif  len(new_subscriptions['directors']) > len(old_subscriptions['directors']):
                    # new_director = set(new_subscriptions['directors']) - set(old_subscriptions['directors'])
                    #dobavi rezisere filma, DECIMAL 
                    film_directors = set(['Actor Actor'])
                    # new_image['feed'][film]['subscription_score'] += (10 if new_director in film_directors else 0)
                    new_image['feed'][film]['subscription_score'] += update_subscription_score(new_subscriptions['directors'], old_subscriptions['directors'], film_directors)
                elif  len(new_subscriptions['genres']) > len(old_subscriptions['genres']):
                    # new_genre = set(new_subscriptions['genres']) - set(old_subscriptions['genres'])
                    #dobavi zanrove filma, DECIMAL 
                    film_genres = set(['Action'])
                    # new_image['feed'][film]['subscription_score'] += (10 if new_genre in film_genres else 0)
                    new_image['feed'][film]['subscription_score'] += update_subscription_score(new_subscriptions['genres'], old_subscriptions['genres'], film_genres)
                elif len(new_subscriptions) < len(old_subscriptions):
                    #obrisao pretplatu
                    # deleted_actor = set(old_subscriptions['actors']) - set(new_subscriptions['actors'])
                    #dobavi glumce filma, DECIMAL 
                    film_actors = set(['Actor Actor'])
                    # new_image['feed'][film]['subscription_score'] -= (10 if deleted_actor in film_actors else 0)
                    new_image['feed'][film]['subscription_score'] -=update_subscription_score(old_subscriptions['actors'], new_subscriptions['actors'], film_actors)
                elif  len(new_subscriptions['directors']) < len(old_subscriptions['directors']):
                    # deleted_director = set(old_subscriptions['directors']) - set(new_subscriptions['directors'])
                    #dobavi rezisere filma, DECIMAL 
                    film_directors = set(['Actor Actor'])
                    # new_image['feed'][film]['subscription_score'] -= (10 if deleted_director in film_directors else 0)
                    new_image['feed'][film]['subscription_score'] -= update_subscription_score(old_subscriptions['directors'], new_subscriptions['directors'], film_directors)
                elif  len(new_subscriptions['genres']) < len(old_subscriptions['genres']):
                    # deleted_genre = set(old_subscriptions['genres']) - set(new_subscriptions['genres'])
                    #dobavi zanrove filma, DECIMAL 
                    film_genres = set(['Action'])
                    # new_image['feed'][film]['subscription_score'] -= (10 if deleted_genre in film_genres else 0)
                    new_image['feed'][film]['subscription_score'] -= update_subscription_score(old_subscriptions['genres'], new_subscriptions['genres'], film_genres)
                
                new_image['feed'][film]['score'] = new_image['feed'][film]['subscription_score'] + new_image['feed'][film]['rating_score'] + new_image['feed'][film]['download_score']

                table.put_item(Item=new_image)

    return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
            },
            'body': json.dumps("Success")
        }
