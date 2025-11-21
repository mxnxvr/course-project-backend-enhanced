from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from django.contrib.sessions.models import Session
from django.utils import timezone

@receiver(user_logged_in)
def remove_other_sessions(sender, user, request, **kwargs):
    """
    Removes other sessions for the same user when they log in.
    This enforces a single-session policy.
    """
    # Get the current session key
    current_session_key = request.session.session_key

    # Iterate through all active sessions
    for session in Session.objects.filter(expire_date__gte=timezone.now()):
        data = session.get_decoded()
        
        # Check if the session belongs to the logged-in user
        # The user ID is stored in the session data under '_auth_user_id'
        if data.get('_auth_user_id') == str(user.id):
            # If the session key is different from the current one, delete it
            if session.session_key != current_session_key:
                session.delete()
