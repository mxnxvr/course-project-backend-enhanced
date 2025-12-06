from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth.models import User
from .models import PlayerData, Score
from .serializers import RegisterSerializer, PlayerDataSerializer, ScoreSerializer, CustomTokenObtainPairSerializer
from rest_framework.permissions import IsAuthenticated
from .permissions import IsSingleSession
from django.shortcuts import get_object_or_404
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import authenticate
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            print(f"DEBUG: Login Error: {type(e).__name__}: {str(e)}")
            import traceback
            traceback.print_exc()
            # If authentication fails, return just the message string
            # We need to extract the message from the exception
            if hasattr(e, 'detail'):
                msg = e.detail
                if isinstance(msg, dict) and 'no_active_account' in msg:
                    return Response(msg['no_active_account'], status=status.HTTP_401_UNAUTHORIZED)
                if isinstance(msg, dict) and 'detail' in msg:
                    return Response(msg['detail'], status=status.HTTP_401_UNAUTHORIZED)
                return Response(str(msg), status=status.HTTP_401_UNAUTHORIZED)
            return Response("Please check the credentials and try again", status=status.HTTP_401_UNAUTHORIZED)

        return Response(serializer.validated_data, status=status.HTTP_200_OK)

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer

class PlayerDataView(APIView):
    permission_classes = [IsAuthenticated, IsSingleSession]

    def get(self, request):
        player, _ = PlayerData.objects.get_or_create(user=request.user)
        serializer = PlayerDataSerializer(player)
        return Response(serializer.data)

    def post(self, request):
        player, _ = PlayerData.objects.get_or_create(user=request.user)
        coins = request.data.get('coins')
        level = request.data.get('level')
        if coins is not None:
            player.coins = int(coins)
        if level is not None:
            player.level = int(level)
        player.save()
        return Response({'message': 'Player data updated successfully!'})

class SubmitScoreView(APIView):
    permission_classes = [IsAuthenticated, IsSingleSession]

    def post(self, request):
        score_value = int(request.data.get('score', 0))
        Score.objects.create(user=request.user, score=score_value)
        return Response({'message': 'Score submitted'})

class LeaderboardView(APIView):
    permission_classes = [IsAuthenticated, IsSingleSession]

    def get(self, request):
        top = Score.objects.all()[:50]
        serializer = ScoreSerializer(top, many=True)
        return Response(serializer.data)

class VerifyEmailView(APIView):
    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
        except (TypeError, ValueError, OverflowError):
            return Response({"error": "Invalid user id"}, status=400)

        user = get_object_or_404(User, pk=uid)

        if user.is_active:
            return Response({"message": "Email already verified!"}, status=200)

        if default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            return Response({"message": "Email verified successfully!"})

        return Response({"error": "Invalid or expired token"}, status=400)

class RequestPasswordResetView(APIView):
    def post(self, request):
        email = request.data.get("email")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=404)

        from .utils import send_password_reset_email
        send_password_reset_email(request, user)

        return Response({"message": "Password reset email sent."})


class ResetPasswordView(APIView):
    def post(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            new_password = request.data.get("password")
            confirm_password = request.data.get("confirm_password")

            if not new_password:
                return Response({"error": "Password required"}, status=400)
            
            if new_password != confirm_password:
                return Response({"error": "Passwords do not match"}, status=400)

            user.set_password(new_password)
            user.save()
            return Response({"message": "Password reset successful."})

        return Response({"error": "Invalid or expired token"}, status=400)
