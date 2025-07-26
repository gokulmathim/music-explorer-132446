from django.db import models
from django.contrib.auth.models import User

class Artist(models.Model):
    """Represents a music artist."""
    name = models.CharField(max_length=100)
    bio = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='artist_images/', blank=True, null=True)

    def __str__(self):
        return self.name

class Album(models.Model):
    """Represents an album released by an Artist."""
    artist = models.ForeignKey(Artist, related_name='albums', on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    cover = models.ImageField(upload_to='album_covers/', blank=True, null=True)
    release_date = models.DateField(blank=True, null=True)

    def __str__(self):
        return f"{self.title} - {self.artist.name}"

class Song(models.Model):
    """Represents a song in the database."""
    title = models.CharField(max_length=100)
    artist = models.ForeignKey(Artist, related_name='songs', on_delete=models.CASCADE)
    album = models.ForeignKey(Album, related_name='songs', on_delete=models.CASCADE, null=True, blank=True)
    file = models.FileField(upload_to='songs/')
    length = models.DurationField(blank=True, null=True)
    genre = models.CharField(max_length=64, blank=True)
    year = models.PositiveIntegerField(blank=True, null=True)

    def __str__(self):
        return f"{self.title} - {self.artist.name}"

class Playlist(models.Model):
    """Custom playlist for users."""
    user = models.ForeignKey(User, related_name='playlists', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    songs = models.ManyToManyField(Song, related_name='playlists')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.user.username})"

class UserProfile(models.Model):
    """Extends Django User with extra preferences."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    favorite_artists = models.ManyToManyField(Artist, blank=True)
    favorite_genres = models.CharField(max_length=256, blank=True)
    avatar = models.ImageField(upload_to='user_avatars/', blank=True, null=True)

    def __str__(self):
        return self.user.username
