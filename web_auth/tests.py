from django.test import TestCase, Client
from django.urls import reverse

class WebAuthTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_verify_email_page(self):
        url = reverse('web-verify-email', kwargs={'uidb64': 'uid', 'token': 'token'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'web_auth/verify_email.html')

    def test_request_reset_page(self):
        url = reverse('web-password-reset-request')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'web_auth/request_reset.html')

    def test_reset_password_page(self):
        url = reverse('web-reset-password', kwargs={'uidb64': 'uid', 'token': 'token'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'web_auth/reset_password.html')
