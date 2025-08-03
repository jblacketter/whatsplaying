import requests
from django.conf import settings
from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)


class TMDbClient:
    def __init__(self):
        self.api_key = settings.TMDB_API_KEY
        self.base_url = settings.TMDB_API_BASE_URL
        self.image_base_url = "https://image.tmdb.org/t/p/"
        
    def _make_request(self, endpoint, params=None):
        """Make a request to the TMDb API"""
        if not self.api_key:
            logger.error("TMDb API key not configured")
            return None
            
        url = f"{self.base_url}{endpoint}"
        if params is None:
            params = {}
        params['api_key'] = self.api_key
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"TMDb API request failed: {e}")
            return None
    
    def search_multi(self, query, page=1):
        """Search for movies and TV shows"""
        cache_key = f"tmdb_search_{query}_{page}"
        cached_result = cache.get(cache_key)
        if cached_result:
            return cached_result
            
        result = self._make_request('/search/multi', {
            'query': query,
            'page': page
        })
        
        if result:
            cache.set(cache_key, result, 3600)  # Cache for 1 hour
        return result
    
    def get_movie_details(self, movie_id):
        """Get detailed information about a movie"""
        cache_key = f"tmdb_movie_{movie_id}"
        cached_result = cache.get(cache_key)
        if cached_result:
            return cached_result
            
        result = self._make_request(f'/movie/{movie_id}', {
            'append_to_response': 'watch/providers,credits,recommendations'
        })
        
        if result:
            cache.set(cache_key, result, 86400)  # Cache for 24 hours
        return result
    
    def get_tv_details(self, tv_id):
        """Get detailed information about a TV show"""
        cache_key = f"tmdb_tv_{tv_id}"
        cached_result = cache.get(cache_key)
        if cached_result:
            return cached_result
            
        result = self._make_request(f'/tv/{tv_id}', {
            'append_to_response': 'watch/providers,credits,recommendations'
        })
        
        if result:
            cache.set(cache_key, result, 86400)  # Cache for 24 hours
        return result
    
    def get_watch_providers(self, media_type, media_id, country='US'):
        """Get watch providers for a movie or TV show"""
        cache_key = f"tmdb_providers_{media_type}_{media_id}_{country}"
        cached_result = cache.get(cache_key)
        if cached_result:
            return cached_result
            
        endpoint = f'/{media_type}/{media_id}/watch/providers'
        result = self._make_request(endpoint)
        
        if result and 'results' in result:
            country_data = result['results'].get(country, {})
            if country_data:
                cache.set(cache_key, country_data, 86400)  # Cache for 24 hours
                return country_data
        return None
    
    def get_trending(self, media_type='all', time_window='week'):
        """Get trending content"""
        cache_key = f"tmdb_trending_{media_type}_{time_window}"
        cached_result = cache.get(cache_key)
        if cached_result:
            return cached_result
            
        result = self._make_request(f'/trending/{media_type}/{time_window}')
        
        if result:
            cache.set(cache_key, result, 3600)  # Cache for 1 hour
        return result
    
    def get_providers_list(self, watch_region='US'):
        """Get list of all available streaming providers"""
        cache_key = f"tmdb_providers_list_{watch_region}"
        cached_result = cache.get(cache_key)
        if cached_result:
            return cached_result
            
        result = self._make_request('/watch/providers/movie', {
            'watch_region': watch_region
        })
        
        if result:
            cache.set(cache_key, result, 604800)  # Cache for 1 week
        return result
    
    def get_image_url(self, path, size='w500'):
        """Get full image URL from path"""
        if not path:
            return None
        return f"{self.image_base_url}{size}{path}"
    
    def search_person(self, query):
        """Search for people (actors, directors, etc.)"""
        cache_key = f"tmdb_search_person_{query}"
        cached_result = cache.get(cache_key)
        if cached_result:
            return cached_result
            
        result = self._make_request('/search/person', {
            'query': query
        })
        
        if result:
            cache.set(cache_key, result, 3600)  # Cache for 1 hour
        return result
    
    def get_person_credits(self, person_id):
        """Get movie and TV credits for a person"""
        cache_key = f"tmdb_person_credits_{person_id}"
        cached_result = cache.get(cache_key)
        if cached_result:
            return cached_result
            
        result = self._make_request(f'/person/{person_id}/combined_credits')
        
        if result:
            cache.set(cache_key, result, 86400)  # Cache for 24 hours
        return result
    
    def discover_movies(self, with_cast=None, with_crew=None, page=1):
        """Discover movies with specific cast or crew members"""
        params = {'page': page}
        
        if with_cast:
            params['with_cast'] = ','.join(map(str, with_cast)) if isinstance(with_cast, list) else str(with_cast)
        
        if with_crew:
            params['with_crew'] = ','.join(map(str, with_crew)) if isinstance(with_crew, list) else str(with_crew)
        
        cache_key = f"tmdb_discover_movies_{with_cast}_{with_crew}_{page}"
        cached_result = cache.get(cache_key)
        if cached_result:
            return cached_result
            
        result = self._make_request('/discover/movie', params)
        
        if result:
            cache.set(cache_key, result, 3600)  # Cache for 1 hour
        return result
    
    def discover_tv(self, with_cast=None, with_crew=None, page=1):
        """Discover TV shows with specific cast or crew members"""
        params = {'page': page}
        
        if with_cast:
            # TMDb uses 'with_people' for TV shows instead of 'with_cast'
            params['with_people'] = ','.join(map(str, with_cast)) if isinstance(with_cast, list) else str(with_cast)
        
        cache_key = f"tmdb_discover_tv_{with_cast}_{with_crew}_{page}"
        cached_result = cache.get(cache_key)
        if cached_result:
            return cached_result
            
        result = self._make_request('/discover/tv', params)
        
        if result:
            cache.set(cache_key, result, 3600)  # Cache for 1 hour
        return result