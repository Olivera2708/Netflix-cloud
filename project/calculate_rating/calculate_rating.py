
def calculate_rating(event, context):
    ratings = event['ratings']
    genres = event['genres']
    rating_score = 0
    for rating in ratings:
        for rating_genre in rating['genres']:
            if rating_genre in genres:
                rating_score += rating['rating']
    result = {
        'rating_score': rating_score,
        'user_id': event['user_id'],
        'movie_id': event['id']
    }
    return result