from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import WatchlistItem
from tmdb.client import TMDbClient
import json


@login_required
def watchlist(request):
    items = request.user.watchlist_items.all()
    
    # Group items by status
    want_to_watch = items.filter(status='want_to_watch')
    watching = items.filter(status='watching')
    watched = items.filter(status='watched')
    
    return render(request, 'watchlist/watchlist.html', {
        'want_to_watch': want_to_watch,
        'watching': watching,
        'watched': watched,
    })


@login_required
@require_POST
def add_to_watchlist(request):
    data = json.loads(request.body)
    
    item, created = WatchlistItem.objects.get_or_create(
        user=request.user,
        tmdb_id=data['tmdb_id'],
        media_type=data['media_type'],
        defaults={
            'title': data['title'],
            'poster_path': data.get('poster_path', ''),
            'release_date': data.get('release_date', ''),
            'overview': data.get('overview', ''),
        }
    )
    
    if created:
        messages.success(request, f'{item.title} added to your watchlist!')
        return JsonResponse({'success': True, 'message': 'Added to watchlist'})
    else:
        return JsonResponse({'success': False, 'message': 'Already in watchlist'})


@login_required
@require_POST
def remove_from_watchlist(request, item_id):
    item = get_object_or_404(WatchlistItem, id=item_id, user=request.user)
    title = item.title
    item.delete()
    messages.success(request, f'{title} removed from your watchlist!')
    return redirect('watchlist')


@login_required
@require_POST
def update_watchlist_status(request, item_id):
    item = get_object_or_404(WatchlistItem, id=item_id, user=request.user)
    new_status = request.POST.get('status')
    
    if new_status in ['want_to_watch', 'watching', 'watched']:
        item.status = new_status
        if new_status == 'watched':
            from django.utils import timezone
            item.watched_date = timezone.now()
        item.save()
        messages.success(request, f'Status updated for {item.title}')
    
    return redirect('watchlist')
