from django import forms

from .models import Avis


class AvisForm(forms.ModelForm):
    class Meta:
        model = Avis
        fields = ['note', 'commentaire']
        widgets = {
            'commentaire': forms.Textarea(attrs={'rows': 3,
                                                 'placeholder': 'Partagez votre avis sur ce produit...'}),
        }
