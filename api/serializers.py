from rest_framework import serializers
from django.contrib.auth.models import User
from .models import PlayerData, Score
from .utils import send_verification_email
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.exceptions import AuthenticationFailed, ValidationError
from django.utils import timezone
from datetime import timedelta
import re
import uuid

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    default_error_messages = {
        'no_active_account': 'Please check the credentials and try again'
    }

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Generate session ID
        session_id = str(uuid.uuid4())

        # Save to PlayerData
        player_data, _ = PlayerData.objects.get_or_create(user=user)
        player_data.session_id = session_id
        player_data.save()

        # Add to token claims
        token['session_id'] = session_id

        return token

    def validate(self, attrs):
        username = attrs.get(self.username_field)
        user = None

        if username:
            user = User.objects.filter(username=username).first()

        if user:
            player_data, _ = PlayerData.objects.get_or_create(user=user)
            
            # Check for lockout
            if player_data.lockout_until and player_data.lockout_until > timezone.now():
                wait_time = (player_data.lockout_until - timezone.now()).seconds // 60 + 1
                raise ValidationError(
                    {"detail": f"Account locked. Try again in {wait_time} minutes."}
                )

        try:
            data = super().validate(attrs)
            
            # Successful login - reset counters
            if user:
                player_data, _ = PlayerData.objects.get_or_create(user=user)
                player_data.failed_login_attempts = 0
                player_data.lockout_until = None
                player_data.save()
                
            return data

        except AuthenticationFailed:
            # Failed login - increment counters
            if user:
                player_data, _ = PlayerData.objects.get_or_create(user=user)
                player_data.failed_login_attempts += 1
                
                if player_data.failed_login_attempts >= 5:
                    player_data.lockout_until = timezone.now() + timedelta(minutes=5)
                    player_data.save()
                    raise ValidationError(
                        {"detail": "So many failed attempts. Account locked for 5 minutes."}
                    )
                
                player_data.save()
            
            raise

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email']


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    email = serializers.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def validate_password(self, value):
        if not any(char.isdigit() for char in value):
            raise serializers.ValidationError("Password must contain at least one digit.")
        if not any(char.isupper() for char in value):
            raise serializers.ValidationError("Password must contain at least one uppercase letter.")
        return value

    def validate_username(self, value):
        if not value.isalnum():
            raise serializers.ValidationError("Username must contain only alphanumeric characters.")
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password']
        )

        # deactivate until email is verified
        user.is_active = False
        user.save()

        # keep player data creation
        PlayerData.objects.create(user=user)

        # send verification link
        send_verification_email(user)

        return user


class PlayerDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlayerData
        fields = ['coins', 'level']


class ScoreSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Score
        fields = ['user', 'score', 'timestamp']
