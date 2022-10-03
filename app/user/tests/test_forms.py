from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone

import datetime

from user.forms import (BearerTokenForm,
                        UserCreateForm,
                        RefreshTokenForm)

from oauth2_provider.models import (get_refresh_token_model,
                                    Application,
                                    get_access_token_model)


class FormsTests(TestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='test@test.com',
            name='testname',
            password='testpassword'
        )

    def test_forms_with_correct_credentails(self):
        bearer_form = BearerTokenForm(data={
            'email': 'test@test.com',
            'password': 'testpassword'
        })

        self.assertTrue(bearer_form.is_valid())

        user_form = UserCreateForm(data={
            'email': 'test@test2.com',
            'name': 'testname2',
            'password': 'testpsss'
        })

        self.assertTrue(user_form.is_valid())

        app = Application.objects.create(
            client_type=Application.CLIENT_CONFIDENTIAL,
            authorization_grant_type=Application.GRANT_PASSWORD,
            name='dummy',
            user=self.user
        )
        refresh_token = get_refresh_token_model().objects.create(
            user=self.user,
            token='secret-refresh-token-key',
            access_token=get_access_token_model().objects.create(
                    user=self.user,
                    token='secret-access-token-key',
                    application=app,
                    expires=timezone.now() + datetime.timedelta(days=1)
                ),
            application=app
        )

        refresh_form = RefreshTokenForm(data={
            'refresh_token': refresh_token.token
        })

        self.assertTrue(refresh_form.is_valid())

    def test_forms_with_incorrect_credentails(self):
        app = Application.objects.create(
            client_type=Application.CLIENT_CONFIDENTIAL,
            authorization_grant_type=Application.GRANT_PASSWORD,
            name='dummy',
            user=self.user
        )

        get_access_token_model().objects.create(
                    user=self.user,
                    token='secret-access-token-key',
                    application=app,
                    expires=timezone.now() + datetime.timedelta(days=1)
                )

        bearer_form = BearerTokenForm(data={
            'email': 'test@test.com',
            'password': 'testpassword'
        })

        self.assertFalse(bearer_form.is_valid())

        bearer_form = BearerTokenForm(data={
            'email': 'test@test.com',
            'password': 'testpass'
        })

        self.assertFalse(bearer_form.is_valid())

        user_form = UserCreateForm(data={
            'email': 'test@test.com',
            'name': 'testname',
            'password': 'testpassword'
        })

        self.assertFalse(user_form.is_valid())

        refresh_form = RefreshTokenForm(data={
            'refresh_token': 'valid-refresh-token'
        })

        self.assertFalse(refresh_form.is_valid())
