from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Artist, Album, Song, Playlist, UserProfile

# PUBLIC_INTERFACE
class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for user profile and preferences."""
    class Meta:
        model = UserProfile
        fields = ('id', 'avatar', 'favorite_artists', 'favorite_genres')
        read_only_fields = ['id']

# PUBLIC_INTERFACE
class UserSerializer(serializers.ModelSerializer):
    """Serializer for Django user."""
    profile = UserProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'profile')
        read_only_fields = ['id', 'profile']

# PUBLIC_INTERFACE
class RegisterSerializer(serializers.ModelSerializer):
    """Serializer for user registration."""
    class Meta:
        model = User
        fields = ('id', 'username', 'password', 'email')
        extra_kwargs = {'password': {'write_only': True}}

    # PUBLIC_INTERFACE
    def create(self, validated_data):
        """Create user with hashed password."""
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password']
        )
        UserProfile.objects.create(user=user)
        return user

# PUBLIC_INTERFACE
class ArtistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Artist
        fields = '__all__'

# PUBLIC_INTERFACE
class AlbumSerializer(serializers.ModelSerializer):
    artist = ArtistSerializer(read_only=True)
    artist_id = serializers.PrimaryKeyRelatedField(
        queryset=Artist.objects.all(), source='artist', write_only=True
    )

    class Meta:
        model = Album
        fields = ['id', 'artist', 'artist_id', 'title', 'cover', 'release_date']

# PUBLIC_INTERFACE
class SongSerializer(serializers.ModelSerializer):
    artist = ArtistSerializer(read_only=True)
    album = AlbumSerializer(read_only=True)
    artist_id = serializers.PrimaryKeyRelatedField(
        queryset=Artist.objects.all(), source='artist', write_only=True
    )
    album_id = serializers.PrimaryKeyRelatedField(
        queryset=Album.objects.all(), source='album', write_only=True, required=False, allow_null=True
    )

    class Meta:
        model = Song
        fields = [
            'id', 'title', 'artist', 'artist_id', 'album', 'album_id',
            'file', 'length', 'genre', 'year'
        ]

# PUBLIC_INTERFACE
class PlaylistSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    songs = SongSerializer(many=True, read_only=True)
    song_ids = serializers.PrimaryKeyRelatedField(
        many=True, write_only=True, queryset=Song.objects.all(), source='songs'
    )

    class Meta:
        model = Playlist
        fields = [
            'id', 'user', 'name', 'description', 'songs', 'song_ids', 'created_at'
        ]
        read_only_fields = ['id', 'user', 'songs', 'created_at']

    # PUBLIC_INTERFACE
    def create(self, validated_data):
        songs = validated_data.pop('songs')
        playlist = Playlist.objects.create(**validated_data)
        playlist.songs.set(songs)
        return playlist

    # PUBLIC_INTERFACE
    def update(self, instance, validated_data):
        songs = validated_data.pop('songs', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if songs is not None:
            instance.songs.set(songs)
        instance.save()
        return instance
