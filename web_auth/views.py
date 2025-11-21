from django.shortcuts import render

def verify_email_view(request, uidb64, token):
    return render(request, 'web_auth/verify_email.html', {
        'uidb64': uidb64,
        'token': token
    })

def request_password_reset_view(request):
    return render(request, 'web_auth/request_reset.html')

def reset_password_view(request, uidb64, token):
    return render(request, 'web_auth/reset_password.html', {
        'uidb64': uidb64,
        'token': token
    })

def home_view(request):
    return render(request, 'web_auth/home.html')
