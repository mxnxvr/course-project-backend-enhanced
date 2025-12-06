from django.urls import reverse
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from .models import PlayerData

class SingleSessionTests(APITestCase):
    def setUp(self):
        self.username = 'testuser'
        self.password = 'testpass123'
        self.user = User.objects.create_user(username=self.username, password=self.password, email='test@example.com')
        # Ensure user is active (RegisterView sets it to False usually)
        self.user.is_active = True
        self.user.save()
        
        # Ensure player data exists (optional, as views often get_or_create)
        PlayerData.objects.create(user=self.user)

    def test_single_session_enforcement(self):
        # 1. First Login
        response1 = self.client.post(reverse('login'), {'username': self.username, 'password': self.password})
        self.assertEqual(response1.status_code, 200)
        token1 = response1.data['access']
        
        # 1.a Verify Token 1 works
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token1)
        response_data1 = self.client.get(reverse('playerdata'))
        self.assertEqual(response_data1.status_code, 200, "Token 1 should work initially")

        # 2. Second Login (New Session)
        response2 = self.client.post(reverse('login'), {'username': self.username, 'password': self.password})
        self.assertEqual(response2.status_code, 200)
        token2 = response2.data['access']
        
        # 3. Verify Token 1 NO LONGER works
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token1)
        response_data_fail = self.client.get(reverse('playerdata'))
        
        # Expect 403 Forbidden because permissions.py returns False
        self.assertEqual(response_data_fail.status_code, 403, "Token 1 should be invalid after second login")
        
        # 4. Verify Token 2 works
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token2)
        response_data2 = self.client.get(reverse('playerdata'))
        self.assertEqual(response_data2.status_code, 200, "Token 2 should work")

    def test_refresh_token_invalidation(self):
        # 1. Login Session 1
        response1 = self.client.post(reverse('login'), {'username': self.username, 'password': self.password})
        token1_access = response1.data['access']
        token1_refresh = response1.data['refresh']

        # 2. Login Session 2
        self.client.post(reverse('login'), {'username': self.username, 'password': self.password})

        # 3. Try to refresh Session 1's token
        # Note: By default, refresh might SUCCEED, but the NEW access token should fail Authorization
        response_refresh = self.client.post(reverse('token_refresh'), {'refresh': token1_refresh})
        
        if response_refresh.status_code == 200:
            # If refresh succeeds, the new access token MUST NOT work
            new_access_token = response_refresh.data['access']
            self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + new_access_token)
            response_data = self.client.get(reverse('playerdata'))
            self.assertEqual(response_data.status_code, 403, "Refreshed token from old session must be invalid")
        else:
            # It's also acceptable if the refresh itself fails (depending on implementation config)
            # But currently we haven't customized RefreshView, so we expect 200 -> 403
            pass
