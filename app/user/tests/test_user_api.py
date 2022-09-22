from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.test import override_settings

from rest_framework.test import APITestCase
from rest_framework import status

from oauth2_provider.models import AccessToken, Application

from datetime import timedelta

from user.tasks import send_reset_password_email

from time import sleep

CREATE_USER_URL = reverse('user:create-user')
HEALTH_CHECK_URL = reverse('health-check')
USER_DETAIL_URL = reverse('user:user-detail')
CHANGE_PASSWORD_URL = reverse('user:password-change')
PASSWORD_RESET_URL = reverse('user:reset-password')


def create_user(**params):
    return get_user_model().objects.create_user(**params)


class PublicUserAPITests(APITestCase):

    def test_create_user_with_valid_credentials(self):
        payload = {
            'email': 'test@test.com',
            'password': 'testpassword',
            'name': 'testusername'
        }

        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        user = get_user_model().objects.get(**res.data)
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)

    def test_user_exists(self):
        payload = {
            'email': 'test@test.com',
            'password': 'testpassword',
            'name': 'testusername'
        }

        create_user(**payload)

        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_id_too_short(self):
        payload = {
            'email': 'test@test.com',
            'password': '1234',
            'name': 'testusername'
        }

        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        user_exists = get_user_model().objects.filter(email=payload['email']) \
            .exists()
        self.assertFalse(user_exists)

    def test_authenticated_views(self):
        payload = {
            'email': 'test@test.com',
            'password': 'testpassword',
            'name': 'testusername'
        }

        user = create_user(**payload)

        app = Application.objects.create(
            client_type=Application.CLIENT_CONFIDENTIAL,
            authorization_grant_type=Application.GRANT_PASSWORD,
            name='dummy',
            user=user
        )

        access_token = AccessToken.objects.create(
            user=user,
            scope='read write',
            expires=timezone.now() + timedelta(seconds=300),
            token='secret-access-token-key',
            application=app
        )

        token = f"Bearer {access_token}"

        res = self.client.get(HEALTH_CHECK_URL, HTTP_AUTHORIZATION=token)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_unauthenticated_request(self):

        res = self.client.get(HEALTH_CHECK_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    @override_settings(
        CACHES={
            'default': {
                'BACKEND': 'django.core.cache.backends.dummy.DummyCache'}})
    def test_reset_password_request(self):
        """
        Test password request with invalid payload
        be inside with normal request becouse I can't
        figure out how do it in other way.
        """
        payload = {'email': ''}

        res = self.client.post(PASSWORD_RESET_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        # Test password request with correct payload

        payload = {'email': 'test@test.com'}

        create_user(
            email=payload['email'],
            password='testpassword',
            name='testname')

        res = self.client.post(PASSWORD_RESET_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_reset_password_sending_mail(self):
        """Test requesting a password reset"""

        res = send_reset_password_email.delay(
            'test subject',
            'test body',
            'test@test.com'
        )
        sleep(5)
        self.assertEqual(res.status, 'SUCCESS')


class AuthenticatedUserAPITests(APITestCase):

    def setUp(self):

        self.user = create_user(
            email='test@test.com',
            name='testusername',
            password='testpassword'
        )
        self.client.force_authenticate(user=self.user)

    def test_retrieve_users_detail(self):

        res = self.client.get(USER_DETAIL_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {
            'email': self.user.email,
            'name': self.user.name
        })

    def test_change_password_correct(self):

        payload = {
            'old_password': 'testpassword',
            'new_password': 'newpassword'
        }

        res = self.client.patch(CHANGE_PASSWORD_URL, payload)

        self.user.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertNotIn('old_passowrd' or 'new_password', res.data)
        self.assertTrue(self.user.check_password(payload['new_password']))

    def test_change_password_with_similar_passwords(self):
        payload = {
            'old_password': 'newpassword',
            'new_password': 'newpassword'
        }

        res = self.client.patch(CHANGE_PASSWORD_URL, payload)

        self.user.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn('old_passowrd' or 'new_password', res.data)
        self.assertFalse(self.user.check_password(payload['new_password']))

    def test_change_password_with_wrong_old_password(self):
        payload = {
            'old_password': 'wrongone',
            'new_password': 'newpassword'
        }

        res = self.client.patch(CHANGE_PASSWORD_URL, payload)

        self.user.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn('old_passowrd' or 'new_password', res.data)
        self.assertFalse(self.user.check_password(payload['new_password']))


class TestThrottling(APITestCase):
    TESTING_THRESHOLD = '5/min'

    def setUp(self):

        create_user(
            email='test@test.com',
            password='testpassword',
            name='testname')

    @override_settings(THROTTLE_THRESHOLD=TESTING_THRESHOLD)
    def test_password_reset_throttling(self):
        payload = {'email': 'test@test.com'}

        for i in range(0, 5):
            self.client.post(PASSWORD_RESET_URL, payload)

        response = self.client.post(PASSWORD_RESET_URL, payload)

        self.assertEqual(
            response.status_code,
            status.HTTP_429_TOO_MANY_REQUESTS)
