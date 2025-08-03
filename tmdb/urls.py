from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('search/', views.search, name='search'),
    path('advanced-search/', views.advanced_search, name='advanced_search'),
]