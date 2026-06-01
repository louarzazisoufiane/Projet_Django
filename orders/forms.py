from django import forms

from .models import Commande


class CheckoutForm(forms.ModelForm):
    """Delivery information collected when validating an order."""

    class Meta:
        model = Commande
        fields = ['nom_complet', 'telephone', 'adresse', 'ville', 'code_postal']
        widgets = {
            'nom_complet': forms.TextInput(attrs={'placeholder': 'Nom et prénom'}),
            'adresse': forms.TextInput(attrs={'placeholder': 'Rue, numéro...'}),
        }
