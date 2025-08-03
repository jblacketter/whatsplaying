from django.db import models
from django.contrib.auth.models import AbstractUser


class StreamingService(models.Model):
    name = models.CharField(max_length=100)
    provider_id = models.IntegerField(unique=True)  # TMDb provider ID
    logo_path = models.CharField(max_length=200, blank=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']


class User(AbstractUser):
    streaming_services = models.ManyToManyField(
        StreamingService,
        related_name='users',
        blank=True
    )
    
    def has_service(self, provider_id):
        return self.streaming_services.filter(provider_id=provider_id).exists()
