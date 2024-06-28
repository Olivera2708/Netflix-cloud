def calculate_downloads(event, context):
    downloaded_genres = event['downloaded_genres']
    movie_genres = set(event['genres'])

    download_score = 0
    for genres in downloaded_genres[-3:]:
        download_score = download_score/2 + len(set(genres) & movie_genres) * 3

    return {
        'download_score': download_score,
        'user_id': event['user_id'],
        'movie_id': event['id']
    }