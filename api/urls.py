from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import (
    RegisterView,
    PlayerDataView,
    SubmitScoreView,
    LeaderboardView,
    VerifyEmailView,
    RequestPasswordResetView,
    ResetPasswordView,
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', TokenObtainPairView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('playerdata/', PlayerDataView.as_view(), name='playerdata'),
    path('score/', SubmitScoreView.as_view(), name='submit_score'),
    path('leaderboard/', LeaderboardView.as_view(), name='leaderboard'),

    # Email verification
    path('verify-email/<uidb64>/<token>/', VerifyEmailView.as_view(), name='verify-email'),

    # Password reset
    path("password-reset-request/", RequestPasswordResetView.as_view(), name="password-reset-request"),
    path("reset-password/<uidb64>/<token>/", ResetPasswordView.as_view(), name="reset-password"),
]

