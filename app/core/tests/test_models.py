from django.test import TestCase
from django.contrib.auth import get_user_model


def sample_user(**params):
    return get_user_model().objects.create_user(**params)


class ModelTests(TestCase):

    def test_create_user_with_email_successful(self):
        params = {
            'email': 'test@test.com',
            'name': 'testusername',
            'password': 'testpassword'
        }

        user = sample_user(**params)

        for key in params.keys():
            if key == 'password':
                self.assertTrue(user.check_password(params[key]))
                continue
            self.assertEqual(params[key], getattr(user, key))

    def test_normalized_email(self):
        params = {
            'email': 'test@TEST.com',
            'name': 'testusername',
            'password': 'testpassword'
        }

        user = sample_user(**params)

        self.assertEqual(user.email, params['email'].lower())

    def test_invalid_email(self):
        with self.assertRaises(ValueError):
            sample_user(email=None, password='testpassword')

    def test_create_superuser(self):
        super_user = get_user_model().objects.create_superuser(
            email='test@admin.com',
            password='testAdminPassword'
        )

        self.assertTrue(super_user.is_staff)
        self.assertTrue(super_user.is_superuser)
