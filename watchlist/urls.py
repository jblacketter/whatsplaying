from django.urls import path
from . import views

urlpatterns = [
    path('', views.watchlist, name='watchlist'),
    path('add/', views.add_to_watchlist, name='add_to_watchlist'),
    path('remove/<int:item_id>/', views.remove_from_watchlist, name='remove_from_watchlist'),
    path('update/<int:item_id>/', views.update_watchlist_status, name='update_watchlist_status'),
]