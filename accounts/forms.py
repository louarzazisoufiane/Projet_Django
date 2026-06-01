"""Forms for registration, login and profile management."""
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from .models import ProfilClient

Utilisateur = get_user_model()


class InscriptionForm(UserCreationForm):
    """Public sign-up form (creates a CLIENT account)."""

    email = forms.EmailField(required=True)
    first_name = forms.CharField(label='Prénom', max_length=150)
    last_name = forms.CharField(label='Nom', max_length=150)

    class Meta:
        model = Utilisateur
        fields = ['first_name', 'last_name', 'email']

    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        if Utilisateur.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('Un compte existe déjà avec cette adresse e-mail.')
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.role = Utilisateur.Role.CLIENT
        if commit:
            user.save()
        return user


class ConnexionForm(AuthenticationForm):
    """Login form using the email address as the username field."""

    username = forms.EmailField(label='Adresse e-mail')


class UtilisateurForm(forms.ModelForm):
    class Meta:
        model = Utilisateur
        fields = ['first_name', 'last_name', 'email']

    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        qs = Utilisateur.objects.filter(email__iexact=email).exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError('Cette adresse e-mail est déjà utilisée.')
        return email


class ProfilClientForm(forms.ModelForm):
    class Meta:
        model = ProfilClient
        fields = ['telephone', 'adresse', 'ville', 'code_postal', 'pays']
