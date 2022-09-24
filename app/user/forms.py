from django import forms
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _


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
