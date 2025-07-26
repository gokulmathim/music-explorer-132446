from django.contrib import admin
from .models import Artist, Album, Song, Playlist, UserProfile

admin.site.register(Artist)
admin.site.register(Album)
admin.site.register(Song)
admin.site.register(Playlist)
admin.site.register(UserProfile)
