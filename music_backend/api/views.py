from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from rest_framework import viewsets, permissions, generics
from django.contrib.auth.models import User
from django.db.models import Q
from django.http import FileResponse, Http404
from .models import Artist, Album, Song, Playlist
from .serializers import (
    UserSerializer,
    RegisterSerializer,
    ArtistSerializer,
    AlbumSerializer,
    SongSerializer,
    PlaylistSerializer,
    UserProfileSerializer
)

# PUBLIC_INTERFACE
@api_view(['GET'])
def health(request):
    """Health check endpoint for API."""
    return Response({"message": "Server is up!"})


# =========================
# AUTH / USER MANAGEMENT
# =========================
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token


# PUBLIC_INTERFACE
class RegisterView(generics.CreateAPIView):
    """Allow a user to register."""
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


# PUBLIC_INTERFACE
class LoginView(ObtainAuthToken):
    """User login, returns auth token."""
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        token = Token.objects.get(key=response.data['token'])
        user = token.user
        return Response({
            'token': token.key,
            'user': UserSerializer(user).data
        })


# PUBLIC_INTERFACE
class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """Get user profile and info."""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return User.objects.filter(id=self.request.user.id)

    @action(detail=False, methods=['get', 'put'], permission_classes=[permissions.IsAuthenticated])
    def profile(self, request):
        """Get or update the authenticated user's profile."""
        if request.method == 'GET':
            serializer = UserProfileSerializer(request.user.profile)
            return Response(serializer.data)
        elif request.method == 'PUT':
            serializer = UserProfileSerializer(request.user.profile, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)


# =========================
# ARTIST/ALBUM/SONG CRUD, BROWSE, SEARCH
# =========================

# PUBLIC_INTERFACE
class ArtistViewSet(viewsets.ModelViewSet):
    """Endpoints for Artists."""
    queryset = Artist.objects.all()
    serializer_class = ArtistSerializer
    permission_classes = [permissions.AllowAny]
    filterset_fields = ['name']

# PUBLIC_INTERFACE
class AlbumViewSet(viewsets.ModelViewSet):
    """Endpoints for Albums."""
    queryset = Album.objects.all()
    serializer_class = AlbumSerializer
    permission_classes = [permissions.AllowAny]
    filterset_fields = ['artist', 'title']

# PUBLIC_INTERFACE
class SongViewSet(viewsets.ModelViewSet):
    """Endpoints for Songs (metadata only). Contains streaming action."""
    queryset = Song.objects.all()
    serializer_class = SongSerializer
    permission_classes = [permissions.AllowAny]
    filterset_fields = ['artist', 'album', 'genre', 'title']

    @action(detail=True, methods=['get'], url_path="stream", permission_classes=[permissions.AllowAny])
    def stream(self, request, pk=None):
        """
        Stream the audio file for a song. Returns audio content.
        Usage: GET /api/songs/<pk>/stream/
        """
        song = self.get_object()
        if not song.file:
            raise Http404("Audio file not found")
        response = FileResponse(song.file.open('rb'), content_type='audio/mpeg')
        response['Content-Disposition'] = f'inline; filename="{song.title}.mp3"'
        return response

    @action(detail=False, methods=['get'], url_path="search", permission_classes=[permissions.AllowAny])
    def search(self, request):
        """
        Search for songs. Query params: q=term
        """
        query = request.GET.get('q', '')
        if not query:
            return Response({"detail": "No search query"}, status=400)
        songs = Song.objects.filter(
            Q(title__icontains=query) |
            Q(artist__name__icontains=query) |
            Q(album__title__icontains=query)
        ).distinct()
        serializer = self.get_serializer(songs, many=True)
        return Response(serializer.data)


# PUBLIC_INTERFACE
class PlaylistViewSet(viewsets.ModelViewSet):
    """Endpoints for Playlists (create, update, view, remove)."""
    queryset = Playlist.objects.all()
    serializer_class = PlaylistSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Playlist.objects.filter(user=self.request.user)
        return Playlist.objects.all()

    @action(detail=True, methods=['post'])
    def add_song(self, request, pk=None):
        """Add a song to a playlist."""
        if not request.user.is_authenticated:
            return Response({'error': 'Authentication credentials were not provided.'}, status=401)
        playlist = self.get_object()
        song_id = request.data.get('song_id')
        if not song_id:
            return Response({'error': 'No song_id provided'}, status=400)
        try:
            song = Song.objects.get(pk=song_id)
        except Song.DoesNotExist:
            return Response({'error': 'Song not found'}, status=404)
        playlist.songs.add(song)
        playlist.save()
        return Response({'message': 'Song added'}, status=200)

    @action(detail=True, methods=['post'])
    def remove_song(self, request, pk=None):
        """Remove a song from a playlist."""
        if not request.user.is_authenticated:
            return Response({'error': 'Authentication credentials were not provided.'}, status=401)
        playlist = self.get_object()
        song_id = request.data.get('song_id')
        if not song_id:
            return Response({'error': 'No song_id provided'}, status=400)
        try:
            song = Song.objects.get(pk=song_id)
        except Song.DoesNotExist:
            return Response({'error': 'Song not found'}, status=404)
        playlist.songs.remove(song)
        playlist.save()
        return Response({'message': 'Song removed'}, status=200)
