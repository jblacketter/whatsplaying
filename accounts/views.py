from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import StreamingService
from .forms import CustomUserCreationForm
from tmdb.client import TMDbClient


def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            login(request, user)
            messages.success(request, f'Welcome {username}!')
            return redirect('profile')
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/signup.html', {'form': form})


@login_required
def profile(request):
    if request.method == 'POST':
        # Handle updating streaming services
        service_ids = request.POST.getlist('services')
        request.user.streaming_services.clear()
        for service_id in service_ids:
            try:
                service = StreamingService.objects.get(provider_id=service_id)
                request.user.streaming_services.add(service)
            except StreamingService.DoesNotExist:
                pass
        messages.success(request, 'Your streaming services have been updated!')
        return redirect('profile')
    
    # Load available streaming services from TMDb if not already in database
    if StreamingService.objects.count() == 0:
        client = TMDbClient()
        providers_data = client.get_providers_list()
        if providers_data and 'results' in providers_data:
            # Add popular streaming services
            popular_providers = {
                8: 'Netflix',
                9: 'Amazon Prime Video',
                15: 'Hulu',
                337: 'Disney Plus',
                384: 'HBO Max',
                531: 'Paramount Plus',
                387: 'Peacock',
                2: 'Apple TV Plus',
            }
            for provider_id, name in popular_providers.items():
                provider_data = next(
                    (p for p in providers_data['results'] if p['provider_id'] == provider_id),
                    None
                )
                if provider_data:
                    StreamingService.objects.get_or_create(
                        provider_id=provider_id,
                        defaults={
                            'name': provider_data['provider_name'],
                            'logo_path': provider_data.get('logo_path', '')
                        }
                    )
    
    all_services = StreamingService.objects.all()
    user_services = request.user.streaming_services.all()
    
    return render(request, 'accounts/profile.html', {
        'all_services': all_services,
        'user_services': user_services,
    })
