import base64
import contextlib
import datetime
import os

from cryptography.fernet import Fernet
from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.sessions.models import Session
from oauth2_provider.models import AccessToken, Application, RefreshToken
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import CustomUserSerializer


class Login(APIView):
    """
    View for obtaining an access token given a username and password.
    """

    permission_classes = [AllowAny]
    serializer_class = CustomUserSerializer

    def secure_generate_token(self, length: int = 30):
        """Generate a cryptographically secure random string."""
        if length <= 0:
            raise ValueError("Token length must be positive")
        key = Fernet.generate_key()
        fernet = Fernet(key)
        token_bytes = os.urandom(length)
        token = fernet.encrypt(token_bytes)
        return token.decode()

    def post(self, request, *args, **kwargs):
        """
        Handle POST requests. Expects a 'username' and 'password' in the request data.
        Returns a 400 Bad Request response if either value is missing or invalid,
        and a 401 Unauthorized response if the credentials are invalid.
        If the credentials are valid, generates and returns a new access token.
        """

        username = request.data.get("username")
        password = request.data.get("password")
        auth_header = request.META.get("HTTP_AUTHORIZATION")

        if not auth_header:
            return Response(
                {"error": "Authorization Header missing"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        secrets = auth_header.split()[1]
        decoded_secrets = base64.b64decode(secrets).decode("utf-8").split(":")
        try:
            application = Application.objects.get(client_id=decoded_secrets[0])
        except Application.DoesNotExist:
            return Response(
                {"error": "Invalid application"}, status=status.HTTP_401_UNAUTHORIZED
            )

        if not username or not password:
            return Response(
                {"error": "Please provide both username and password"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = authenticate(request=request, username=username, password=password)
        if not user:
            return Response(
                {"error": "Invalid Credentials"}, status=status.HTTP_401_UNAUTHORIZED
            )

        if user is not None:
            with contextlib.suppress(AccessToken.DoesNotExist):
                token = AccessToken.objects.get(user=user)
                if token:
                    refresh_token = RefreshToken.objects.get(access_token=token.id)
                    refresh_token.delete()
                    token.delete()

            new_token = self.secure_generate_token()
            token_expire = settings.OAUTH2_PROVIDER["ACCESS_TOKEN_EXPIRE_SECONDS"]
            token = AccessToken.objects.create(
                user=user,
                token=new_token,
                application=application,
                expires=datetime.datetime.now()
                + datetime.timedelta(seconds=token_expire),
                scope="read write",
            )

            refresh_token = self.secure_generate_token()
            RefreshToken.objects.create(
                user=user,
                token=refresh_token,
                access_token=token,
                application=application,
            )

        return Response(
            {
                "access_token": token.token,
                "expires_in": token_expire,
                "token_type": "Bearer",
                "scope": token.scope,
                "refresh_token": refresh_token,
            },
            status=status.HTTP_200_OK,
        )


class Logout(APIView):
    """
    View for revoking an access token and logging out the associated user.
    """

    permission_classes = [AllowAny]
    serializer_class = CustomUserSerializer

    def post(self, request, *args, **kwargs):
        """
        Handle POST requests. Expects a valid access token in the request header.
        Returns a 400 Bad Request response if the access token is missing or invalid,
        and a 200 OK response if the token is successfully revoked.
        """
        try:
            token = AccessToken.objects.get(token=request.auth)
        except AccessToken.DoesNotExist:
            return Response(
                {"error": "Invalid access token"}, status=status.HTTP_400_BAD_REQUEST
            )

        refresh_token = RefreshToken.objects.get(access_token=token.id)
        refresh_token.delete()
        token.delete()
        sessions = Session.objects.filter(expire_date__gte=datetime.datetime.now())

        for session in sessions:
            session_data = session.get_decoded()
            if token.user_id == int(session_data.get("_auth_user_id")):
                session.delete()
        return Response(
            {"message": "Logged out successfully"}, status=status.HTTP_200_OK
        )
