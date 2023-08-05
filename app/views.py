from django.shortcuts import render
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.throttling import UserRateThrottle
from rest_framework.views import APIView
from rest_framework import status

from app.utils import create_model_instance, update_or_create_model_instance
from app.models import Location, Event, Song, SongRequest


class DailyUserThrottle(UserRateThrottle):
    rate = '3/day'


class LoginView(APIView):
    """
    Authenticate user and return a token.
    """
    authentication_classes = []
    permission_classes = []

    def post(self, request, format=None):
        email = request.data.get('email')
        password = request.data.get('password')
        user = authenticate(request, email=email, password=password)
        if user is not None:
            token, _ = Token.objects.get_or_create(user=user)
            return Response({'token': token.key}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid username or password.'}, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    """
    Logout the user.
    """
    def get(self, request, format=None):
        request.user.auth_token.delete()
        return Response({'message': 'Successfully logged out'}, status=status.HTTP_200_OK)


class HomeView(APIView):
    """
    Render the home page.
    """
    def get(self, request, format=None):
        return render(request, 'home.html')


class CreateLocationView(APIView):
    """
    Create a new location
    """
    throttle_classes = [DailyUserThrottle]

    def post(self, request, format=None):
        user = request.user
        if not user.is_dj:
            return Response({"error": "User is not a DJ"}, status=status.HTTP_403_FORBIDDEN)

        location = create_model_instance(request.data, Location)
        return Response({"success": f"Location {location.name} created successfully"}, status=status.HTTP_201_CREATED)


class CreateEventView(APIView):
    """
    Create a new event
    """
    throttle_classes = [DailyUserThrottle]

    def post(self, request, format=None):
        user = request.user
        if not user.is_dj:
            return Response({"error": "User is not a DJ"}, status=status.HTTP_403_FORBIDDEN)

        event = create_model_instance(request.data, Event)
        return Response({"success": f"Event {event.name} created successfully"}, status=status.HTTP_201_CREATED)


class CreateSongRequestView(APIView):
    """
    Create a new song and song request.
    """
    authentication_classes = []
    permission_classes = []

    def post(self, request, format=None):
        song_request_data = request.data
        song_data = request.data.pop('song', {})
        song = update_or_create_model_instance(song_data, Song)

        song_request_data['song'] = song.id
        song_request = create_model_instance(song_request_data, SongRequest)

        return Response(
            {"success": f"Song request {song_request.id} was created successfully"}, 
            status=status.HTTP_201_CREATED
        )