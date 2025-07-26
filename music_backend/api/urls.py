from django.urls import path, include
from rest_framework import routers
from .views import (
    health, RegisterView, LoginView,
    UserViewSet, ArtistViewSet, AlbumViewSet, SongViewSet, PlaylistViewSet
)

router = routers.DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'artists', ArtistViewSet, basename='artist')
router.register(r'albums', AlbumViewSet, basename='album')
router.register(r'songs', SongViewSet, basename='song')
router.register(r'playlists', PlaylistViewSet, basename='playlist')

urlpatterns = [
    path('health/', health, name='Health'),
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('', include(router.urls)),
]
