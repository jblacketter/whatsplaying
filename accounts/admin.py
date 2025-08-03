from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, StreamingService


@admin.register(StreamingService)
class StreamingServiceAdmin(admin.ModelAdmin):
    list_display = ['name', 'provider_id']
    search_fields = ['name']


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Streaming Services', {'fields': ('streaming_services',)}),
    )
    filter_horizontal = ('streaming_services',)
