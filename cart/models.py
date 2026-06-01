"""Shopping cart models: Panier and LignePanier."""
from django.conf import settings
from django.db import models

from products.models import Produit


class Panier(models.Model):
    """A client's shopping cart (one active cart per user)."""

    utilisateur = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='panier',
    )
    cree_le = models.DateTimeField(auto_now_add=True)
    modifie_le = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'paniers'
        verbose_name = 'Panier'
        verbose_name_plural = 'Paniers'

    def __str__(self):
        return f'Panier de {self.utilisateur.get_short_name()}'

    @property
    def montant_total(self):
        return sum((ligne.sous_total for ligne in self.lignes.all()), 0)

    @property
    def nombre_articles(self):
        return sum(ligne.quantite for ligne in self.lignes.all())


class LignePanier(models.Model):
    """A product line inside a cart, with its quantity."""

    panier = models.ForeignKey(Panier, on_delete=models.CASCADE, related_name='lignes')
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE, related_name='lignes_panier')
    quantite = models.PositiveIntegerField('quantité', default=1)
    ajoute_le = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'lignes_panier'
        verbose_name = 'Ligne de panier'
        verbose_name_plural = 'Lignes de panier'
        unique_together = ['panier', 'produit']

    def __str__(self):
        return f'{self.produit.nom} × {self.quantite}'

    @property
    def sous_total(self):
        return self.produit.prix * self.quantite
