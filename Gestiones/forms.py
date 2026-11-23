from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.password_validation import MinimumLengthValidator, validate_password
from django.core.exceptions import ValidationError
from django.utils import timezone

from .models import CitaPeluqueria


class InicioSesionForm(AuthenticationForm):
    username = forms.CharField(
        label='Usuario',
        widget=forms.TextInput(attrs={'class': 'form-control', 'autofocus': True}),
    )
    password = forms.CharField(
        label='Contraseña',
        strip=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
    )


def validar_nombre_usuario(value):
    if not value.isalnum():
        raise forms.ValidationError('Usa solo letras y números, sin espacios ni símbolos.')


class RegistroClienteForm(UserCreationForm):
    username = forms.CharField(
        label='Nombre de usuario',
        min_length=3,
        max_length=20,
        validators=[validar_nombre_usuario],
        widget=forms.TextInput(attrs={'class': 'form-control', 'autocomplete': 'username'}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'Nombre de usuario'
        self.fields['password1'].label = 'Contraseña'
        self.fields['password2'].label = 'Confirmar contraseña'
        self.fields['password1'].help_text = 'Usa una contraseña de al menos 6 caracteres.'
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'autocomplete': 'username',
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'autocomplete': 'new-password',
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'autocomplete': 'new-password',
        })

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2:
            if password1 != password2:
                self.add_error(
                    'password2',
                    ValidationError(self.error_messages['password_mismatch'], code='password_mismatch'),
                )
        return password2

    def _post_clean(self):
        forms.ModelForm._post_clean(self)
        password = self.cleaned_data.get('password2')
        if password:
            try:
                validate_password(
                    password,
                    self.instance,
                    password_validators=[MinimumLengthValidator(min_length=6)],
                )
            except ValidationError as error:
                self.add_error('password2', error)


class CitaPeluqueriaForm(forms.ModelForm):
    class Meta:
        model = CitaPeluqueria
        fields = (
            'nombre_dueno',
            'nombre_mascota',
            'telefono',
            'correo_electronico',
            'fecha',
            'hora',
        )
        widgets = {
            'nombre_dueno': forms.TextInput(attrs={'class': 'form-control'}),
            'nombre_mascota': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono': forms.TelInput(attrs={'class': 'form-control'}),
            'correo_electronico': forms.EmailInput(attrs={'class': 'form-control'}),
            'fecha': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'hora': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
        }

    def clean_fecha(self):
        fecha = self.cleaned_data['fecha']
        if fecha < timezone.localdate():
            raise forms.ValidationError('La fecha de la cita no puede estar en el pasado.')
        return fecha
