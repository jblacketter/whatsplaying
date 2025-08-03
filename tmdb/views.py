from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .client import TMDbClient
from watchlist.models import WatchlistItem


def search(request):
    query = request.GET.get('q', '')
    results = []
    user_watchlist_ids = []
    
    if request.user.is_authenticated:
        user_watchlist_ids = list(
            request.user.watchlist_items.values_list('tmdb_id', flat=True)
        )
    
    if query:
        client = TMDbClient()
        search_results = client.search_multi(query)
        
        if search_results and 'results' in search_results:
            for item in search_results['results']:
                if item.get('media_type') in ['movie', 'tv']:
                    # Get watch providers
                    providers = client.get_watch_providers(
                        item['media_type'],
                        item['id']
                    )
                    
                    # Check if available on user's services
                    available_on_user_services = []
                    if request.user.is_authenticated and providers:
                        user_service_ids = list(
                            request.user.streaming_services.values_list('provider_id', flat=True)
                        )
                        
                        if 'flatrate' in providers:
                            for provider in providers['flatrate']:
                                if provider['provider_id'] in user_service_ids:
                                    available_on_user_services.append(provider['provider_name'])
                    
                    results.append({
                        'id': item['id'],
                        'title': item.get('title') or item.get('name'),
                        'media_type': item['media_type'],
                        'poster_path': client.get_image_url(item.get('poster_path')),
                        'release_date': item.get('release_date') or item.get('first_air_date'),
                        'overview': item.get('overview'),
                        'in_watchlist': item['id'] in user_watchlist_ids,
                        'providers': providers,
                        'available_on_user_services': available_on_user_services,
                    })
    
    return render(request, 'tmdb/search.html', {
        'query': query,
        'results': results,
    })


def home(request):
    client = TMDbClient()
    trending = client.get_trending('all', 'week')
    
    trending_items = []
    if trending and 'results' in trending:
        for item in trending['results'][:12]:  # Show top 12
            if item.get('media_type') in ['movie', 'tv']:
                trending_items.append({
                    'id': item['id'],
                    'title': item.get('title') or item.get('name'),
                    'media_type': item['media_type'],
                    'poster_path': client.get_image_url(item.get('poster_path')),
                    'release_date': item.get('release_date') or item.get('first_air_date'),
                })
    
    return render(request, 'tmdb/home.html', {
        'trending_items': trending_items,
    })


def advanced_search(request):
    """Search for movies/TV shows by actors or directors"""
    people_query = request.GET.get('people', '')
    search_type = request.GET.get('type', 'both')  # movie, tv, or both
    results = []
    people_found = []
    
    if people_query:
        client = TMDbClient()
        
        # Parse the input - split by comma or "and"
        people_names = [name.strip() for name in people_query.replace(' and ', ',').split(',')]
        person_ids = []
        
        # Search for each person and get their ID
        for name in people_names:
            if name:
                person_result = client.search_person(name)
                if person_result and 'results' in person_result and person_result['results']:
                    # Take the first result (most relevant)
                    person = person_result['results'][0]
                    person_ids.append(person['id'])
                    people_found.append({
                        'id': person['id'],
                        'name': person['name'],
                        'profile_path': client.get_image_url(person.get('profile_path'), 'w185'),
                        'known_for_department': person.get('known_for_department', 'Acting')
                    })
        
        # Get movies/TV shows with ALL specified people
        if person_ids:
            all_movies = set()
            all_tv_shows = set()
            
            # For each person, get their credits
            for i, person_id in enumerate(person_ids):
                credits = client.get_person_credits(person_id)
                if credits:
                    # Get movies this person is in
                    person_movies = set()
                    if 'cast' in credits:
                        for item in credits['cast']:
                            if 'id' in item and item.get('media_type') == 'movie':
                                person_movies.add(item['id'])
                    if 'crew' in credits:
                        for item in credits['crew']:
                            if 'id' in item and item.get('media_type') == 'movie' and item.get('job') == 'Director':
                                person_movies.add(item['id'])
                    
                    # Get TV shows this person is in
                    person_tv = set()
                    if 'cast' in credits:
                        for item in credits['cast']:
                            if 'id' in item and item.get('media_type') == 'tv':
                                person_tv.add(item['id'])
                    
                    # For the first person, initialize the sets
                    if i == 0:
                        all_movies = person_movies
                        all_tv_shows = person_tv
                    else:
                        # Find intersection with previous results
                        all_movies = all_movies.intersection(person_movies)
                        all_tv_shows = all_tv_shows.intersection(person_tv)
            
            # Get details for the matching content
            user_watchlist_ids = []
            if request.user.is_authenticated:
                user_watchlist_ids = list(
                    request.user.watchlist_items.values_list('tmdb_id', flat=True)
                )
            
            # Process movies
            if search_type in ['movie', 'both'] and all_movies:
                for movie_id in list(all_movies)[:20]:  # Limit to 20 results
                    movie = client.get_movie_details(movie_id)
                    if movie:
                        providers = client.get_watch_providers('movie', movie_id)
                        available_on_user_services = []
                        
                        if request.user.is_authenticated and providers:
                            user_service_ids = list(
                                request.user.streaming_services.values_list('provider_id', flat=True)
                            )
                            if 'flatrate' in providers:
                                for provider in providers['flatrate']:
                                    if provider['provider_id'] in user_service_ids:
                                        available_on_user_services.append(provider['provider_name'])
                        
                        results.append({
                            'id': movie['id'],
                            'title': movie.get('title'),
                            'media_type': 'movie',
                            'poster_path': client.get_image_url(movie.get('poster_path')),
                            'release_date': movie.get('release_date'),
                            'overview': movie.get('overview'),
                            'in_watchlist': movie['id'] in user_watchlist_ids,
                            'available_on_user_services': available_on_user_services,
                            'vote_average': movie.get('vote_average', 0)
                        })
            
            # Process TV shows
            if search_type in ['tv', 'both'] and all_tv_shows:
                for tv_id in list(all_tv_shows)[:20]:  # Limit to 20 results
                    tv = client.get_tv_details(tv_id)
                    if tv:
                        providers = client.get_watch_providers('tv', tv_id)
                        available_on_user_services = []
                        
                        if request.user.is_authenticated and providers:
                            user_service_ids = list(
                                request.user.streaming_services.values_list('provider_id', flat=True)
                            )
                            if 'flatrate' in providers:
                                for provider in providers['flatrate']:
                                    if provider['provider_id'] in user_service_ids:
                                        available_on_user_services.append(provider['provider_name'])
                        
                        results.append({
                            'id': tv['id'],
                            'title': tv.get('name'),
                            'media_type': 'tv',
                            'poster_path': client.get_image_url(tv.get('poster_path')),
                            'release_date': tv.get('first_air_date'),
                            'overview': tv.get('overview'),
                            'in_watchlist': tv['id'] in user_watchlist_ids,
                            'available_on_user_services': available_on_user_services,
                            'vote_average': tv.get('vote_average', 0)
                        })
            
            # Sort by rating
            results.sort(key=lambda x: x.get('vote_average', 0), reverse=True)
    
    return render(request, 'tmdb/advanced_search.html', {
        'people_query': people_query,
        'search_type': search_type,
        'results': results,
        'people_found': people_found,
    })
