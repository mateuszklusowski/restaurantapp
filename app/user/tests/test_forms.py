from django.test import TestCase
from django.contrib.auth import get_user_model

from user.forms import (BearerTokenForm)


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

    def test_forms_with_incorrect_credentails(self):
        bearer_form = BearerTokenForm(data={
            'email': 'test@test.com',
            'password': 'testpass'
        })

        self.assertFalse(bearer_form.is_valid())
