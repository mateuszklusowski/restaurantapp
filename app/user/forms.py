from django import forms
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from oauth2_provider.models import get_refresh_token_model


class BearerTokenForm(forms.Form):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'placeholder': 'Enter email'})
    )
    password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={'placeholder': 'Enter password'})
    )

    def clean(self):
        email = self.cleaned_data['email']
        password = self.cleaned_data['password']

        user = get_user_model().objects.filter(email=email)

        if not user.exists():
            msg = _('Wrong credentials')
            raise forms.ValidationError(msg)

        if not user.first().check_password(password):
            msg = _('Wrong credentials')
            raise forms.ValidationError(msg)


class UserCreateForm(forms.ModelForm):

    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'placeholder': 'Enter email'})
    )
    password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={'placeholder': 'Enter password'})
    )
    name = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Enter username'})
    )

    class Meta:
        model = get_user_model()
        fields = ('email', 'name', 'password')


class RefreshTokenForm(forms.Form):
    refresh_token = forms.CharField(
        required=True,
        widget=forms.PasswordInput(
            attrs={'placeholder': 'Enter refresh token'})
    )

    def clean_refresh_token(self):
        refresh_token = self.cleaned_data['refresh_token']

        token_exists = get_refresh_token_model().objects\
            .filter(token=refresh_token).exists()

        if not token_exists:
            msg = _('Wrong credentials')
            raise forms.ValidationError(msg)

        return refresh_token
