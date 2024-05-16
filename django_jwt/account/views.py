from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenRefreshView

from .serializers import UserSerializer
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from .models import User
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken, TokenError
from rest_framework import status


class RegisterView(APIView):
    @staticmethod
    def post(request):
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class LoginView(APIView):
    @staticmethod
    def post(request):
        email = request.data["email"]
        password = request.data["password"]

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise AuthenticationFailed("Account does  not exist")
        if user is None:
            raise AuthenticationFailed("User does not exist")
        if not user.check_password(password):
            raise AuthenticationFailed("Incorrect Password")

        access_token = str(AccessToken.for_user(user))
        refresh_token = str(RefreshToken.for_user(user))

        response = Response()

        response.set_cookie(key='access_token', value=access_token, httponly=True)
        response.set_cookie(key='refresh_token', value=refresh_token, httponly=True)
        response.data = {
            "access_token": access_token,
            "refresh_token": refresh_token
        }

        return response


class LogoutView(APIView):
    @staticmethod
    def post(request):
        try:
            refresh_token = request.COOKIES.get('refresh_token')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()

                response = Response()
                response.delete_cookie('access_token')
                response.delete_cookie('refresh_token')
                response.data = {
                    "message": "Logout Successful"
                }
                return response
        except TokenError:
            raise AuthenticationFailed("Invalid Token")


class CustomTokenRefreshView(APIView):

    @staticmethod
    def post(request):
        refresh_token = request.COOKIES.get('refresh_token')

        if not refresh_token:
            return Response({"detail": "Please Login First!"}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            refresh_token = RefreshToken(refresh_token)
            access_token = refresh_token.access_token
            response = Response({"detail": "Success"}, status=status.HTTP_200_OK)
            response.set_cookie(
                'access_token',
                access_token,
                httponly=True
            )
            return response
        except TokenError:
            raise AuthenticationFailed("Invalid Token")


class UserView(APIView):

    @staticmethod
    def get(request):
        access_token = request.COOKIES.get('access_token')
        refresh_token = request.COOKIES.get('refresh_token')

        if not refresh_token:
            raise AuthenticationFailed('Please Login First!')
        if not access_token:
            raise AuthenticationFailed('Unauthenticated!')

        try:
            access_token = AccessToken(access_token)
            # Get the user ID from the token payload
            user_id = access_token['user_id']
        except Exception as e:
            raise AuthenticationFailed('Unauthenticated!')
        user = User.objects.filter(id=user_id).first()
        serializer = UserSerializer(user)
        return Response(serializer.data)
