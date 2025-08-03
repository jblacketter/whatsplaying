from django.db import models
from django.conf import settings


class WatchlistItem(models.Model):
    MEDIA_TYPES = (
        ('movie', 'Movie'),
        ('tv', 'TV Show'),
    )
    
    STATUS_CHOICES = (
        ('want_to_watch', 'Want to Watch'),
        ('watching', 'Watching'),
        ('watched', 'Watched'),
    )
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='watchlist_items'
    )
    tmdb_id = models.IntegerField()
    media_type = models.CharField(max_length=10, choices=MEDIA_TYPES)
    title = models.CharField(max_length=200)
    poster_path = models.CharField(max_length=200, blank=True)
    release_date = models.CharField(max_length=20, blank=True)
    overview = models.TextField(blank=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='want_to_watch'
    )
    rating = models.IntegerField(null=True, blank=True)  # User's personal rating (1-10)
    notes = models.TextField(blank=True)
    added_date = models.DateTimeField(auto_now_add=True)
    watched_date = models.DateTimeField(null=True, blank=True)
    
    # Cache provider information
    available_providers = models.JSONField(default=dict, blank=True)
    last_provider_check = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ['user', 'tmdb_id', 'media_type']
        ordering = ['-added_date']
    
    def __str__(self):
        return f"{self.title} ({self.get_media_type_display()})"
    
    def get_poster_url(self):
        if self.poster_path:
            return f"https://image.tmdb.org/t/p/w500{self.poster_path}"
        return None
