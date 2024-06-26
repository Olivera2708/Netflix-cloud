def calculate_subscription(event, context):
    subscribed_actiors = set(event['subscriptions']['actors'])
    subscribed_genres = set(event['subscriptions']['genres'])
    subscribed_directors = set(event['subscriptions']['directors'])

    movie_actiors = set(event['actors'])
    movie_genres = set(event['genres'])
    movie_directors = set(event['directors'])

    subscription_score = (len(subscribed_actiors & movie_actiors) + len(subscribed_directors & movie_directors) + len(subscribed_genres & movie_genres)) * 10
    
    return {
        'subscription_score': subscription_score,
        'user_id': event['user_id'],
        'movie_id': event['id']
    }