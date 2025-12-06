from rest_framework import serializers
from django.contrib.auth.models import User
from .models import PlayerData, Score
from .utils import send_verification_email
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
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
