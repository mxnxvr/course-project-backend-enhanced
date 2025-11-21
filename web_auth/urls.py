from django.urls import path
from . import views

urlpatterns = [
    path('verify-email/<str:uidb64>/<str:token>/', views.verify_email_view, name='web-verify-email'),
    path('password-reset-request/', views.request_password_reset_view, name='web-password-reset-request'),
    path('reset-password/<str:uidb64>/<str:token>/', views.reset_password_view, name='web-reset-password'),
    path('', views.home_view, name='home'),
]
