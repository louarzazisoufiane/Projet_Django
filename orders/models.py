"""Order models: Commande and LigneCommande."""
from django.conf import settings
from django.db import models

from products.models import Produit


class Commande(models.Model):
    """An order validated by a client."""

    class Statut(models.TextChoices):
        EN_ATTENTE = 'EN_ATTENTE', 'En attente'
        CONFIRMEE = 'CONFIRMEE', 'Confirmée'
        EN_PREPARATION = 'EN_PREPARATION', 'En préparation'
        EXPEDIEE = 'EXPEDIEE', 'Expédiée'
        LIVREE = 'LIVREE', 'Livrée'
        ANNULEE = 'ANNULEE', 'Annulée'

    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='commandes',
        verbose_name='client',
    )
    statut = models.CharField(max_length=20, choices=Statut.choices, default=Statut.EN_ATTENTE)
    montant_total = models.DecimalField('montant total', max_digits=10, decimal_places=2, default=0)

    # Delivery snapshot (taken from the client's profile at checkout time).
    nom_complet = models.CharField('nom complet', max_length=255, blank=True)
    telephone = models.CharField('téléphone', max_length=30, blank=True)
    adresse = models.CharField('adresse', max_length=255, blank=True)
    ville = models.CharField('ville', max_length=120, blank=True)
    code_postal = models.CharField('code postal', max_length=20, blank=True)

    date_commande = models.DateTimeField('date de commande', auto_now_add=True)
    modifie_le = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'commandes'
        verbose_name = 'Commande'
        verbose_name_plural = 'Commandes'
        ordering = ['-date_commande']

    def __str__(self):
        return f'Commande #{self.pk} — {self.client.get_short_name()} — {self.get_statut_display()}'

    def recalculer_total(self):
        self.montant_total = sum((ligne.sous_total for ligne in self.lignes.all()), 0)
        return self.montant_total

    @property
    def nombre_articles(self):
        return sum(ligne.quantite for ligne in self.lignes.all())


class LigneCommande(models.Model):
    """A product line attached to an order."""

    commande = models.ForeignKey(Commande, on_delete=models.CASCADE, related_name='lignes')
    produit = models.ForeignKey(
        Produit,
        on_delete=models.SET_NULL,
        null=True,
        related_name='lignes_commande',
    )
    # Snapshots so the order stays accurate even if the product changes/disappears.
    nom_produit = models.CharField(max_length=255)
    prix_unitaire = models.DecimalField('prix unitaire', max_digits=10, decimal_places=2)
    quantite = models.PositiveIntegerField('quantité')

    class Meta:
        db_table = 'lignes_commande'
        verbose_name = 'Ligne de commande'
        verbose_name_plural = 'Lignes de commande'

    def __str__(self):
        return f'{self.nom_produit} × {self.quantite}'

    @property
    def sous_total(self):
        return self.prix_unitaire * self.quantite
