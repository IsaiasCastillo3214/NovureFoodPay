from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


class FoodPayLoginForm(AuthenticationForm):
    username = forms.CharField(
        label='Usuario',
        widget=forms.TextInput(attrs={
            'class': 'foodpay-login-input',
            'placeholder': 'Ingresa tu usuario',
            'autocomplete': 'username',
            'autofocus': True,
        })
    )

    password = forms.CharField(
        label='Contraseña',
        strip=False,
        widget=forms.PasswordInput(attrs={
            'class': 'foodpay-login-input',
            'placeholder': 'Ingresa tu contraseña',
            'autocomplete': 'current-password',
        })
    )

    remember_me = forms.BooleanField(
        label='Recordarme',
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'foodpay-login-check',
        })
    )

    error_messages = {
        'invalid_login': (
            'Usuario o contraseña incorrectos. '
            'Verifica tus datos e inténtalo nuevamente.'
        ),
        'inactive': 'Este usuario se encuentra inactivo. Contacta al administrador.',
    }

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username and password:
            username = username.strip()

            user_obj = User.objects.filter(username__iexact=username).first()

            if not user_obj:
                raise ValidationError(
                    self.error_messages['invalid_login'],
                    code='invalid_login',
                )

            self.user_cache = authenticate(
                self.request,
                username=user_obj.get_username(),
                password=password
            )

            if self.user_cache is None:
                raise ValidationError(
                    self.error_messages['invalid_login'],
                    code='invalid_login',
                )

            self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data