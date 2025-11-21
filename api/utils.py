from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator


def send_verification_email(user):
    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)

    verification_url = "https://manar.rocks" + reverse(
        "web-verify-email",
        kwargs={"uidb64": uidb64, "token": token}
    )

    subject = "Verify Your Email"
    message = f"Click the link to verify your account:\n\n{verification_url}"

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=False,
    )


def send_password_reset_email(request, user):
    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)

    reset_url = "https://" + request.get_host() + reverse(
        "web-reset-password",
        kwargs={"uidb64": uidb64, "token": token}
    )

    subject = "Reset your password"
    message = f"Click here to reset your password:\n\n{reset_url}"

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=False,
    )

