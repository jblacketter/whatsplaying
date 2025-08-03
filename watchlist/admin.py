from django.contrib import admin
from .models import WatchlistItem


@admin.register(WatchlistItem)
class WatchlistItemAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'media_type', 'status', 'added_date']
    list_filter = ['media_type', 'status', 'added_date']
    search_fields = ['title', 'user__username']
    readonly_fields = ['added_date']
