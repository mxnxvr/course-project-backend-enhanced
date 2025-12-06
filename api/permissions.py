from rest_framework import permissions
from .models import PlayerData
import sys

class IsSingleSession(permissions.BasePermission):
    message = "This session has expired. You have logged in from another device."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        # Get session_id from token (request.auth is the AccessToken object)
        try:
            token_session_id = request.auth.get('session_id')
        except AttributeError:
            return False

        if not token_session_id:
            return False

        # Check against DB
        try:
            player_data = request.user.playerdata
            print(f"DEBUG: User: {request.user.username}, DB Session: {player_data.session_id}, Token Session: {token_session_id}", flush=True)
            if str(player_data.session_id) != str(token_session_id):
                print("DEBUG: Session Mismatch! Denying access.", flush=True)
                sys.stdout.flush()
                return False
        except PlayerData.DoesNotExist:
            print("DEBUG: PlayerData not found", flush=True)
            sys.stdout.flush()
            return False

        return True
