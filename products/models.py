"""
Catalog models: Categorie, Produit and Avis.

Field set follows section 6 of the project specification:
nom, description, prix, image, catégorie, quantité en stock,
disponibilité, date d'ajout and note moyenne (via les avis).
"""
from django.conf import settings
from django.db import models
from django.db.models import Avg
from django.urls import reverse
from django.utils.text import slugify

from .validators import valider_extension_image, valider_taille_image


class Categorie(models.Model):
    nom = models.CharField('nom', max_length=150, unique=True)
    slug = models.SlugField(max_length=170, unique=True, blank=True)
    description = models.TextField('description', blank=True)
    image = models.ImageField(
        'image', upload_to='categories/', blank=True, null=True,
        validators=[valider_extension_image, valider_taille_image],
    )
    cree_le = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'categories'
        verbose_name = 'Catégorie'
        verbose_name_plural = 'Catégories'
        ordering = ['nom']

    def __str__(self):
        return self.nom

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nom)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('products:catalogue') + f'?categorie={self.slug}'


class Produit(models.Model):
    nom = models.CharField('nom du produit', max_length=255)
    slug = models.SlugField(max_length=275, unique=True, blank=True)
    description = models.TextField('description', blank=True)
    prix = models.DecimalField('prix', max_digits=10, decimal_places=2)
    image = models.ImageField(
        'image', upload_to='produits/', blank=True, null=True,
        validators=[valider_extension_image, valider_taille_image],
    )
    categorie = models.ForeignKey(
        Categorie,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='produits',
        verbose_name='catégorie',
    )
    quantite_stock = models.PositiveIntegerField('quantité en stock', default=0)
    disponible = models.BooleanField('disponibilité', default=True)
    date_ajout = models.DateTimeField("date d'ajout", auto_now_add=True)
    modifie_le = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'produits'
        verbose_name = 'Produit'
        verbose_name_plural = 'Produits'
        ordering = ['-date_ajout']

    def __str__(self):
        return self.nom

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.nom) or 'produit'
            slug = base
            i = 1
            while Produit.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f'{base}-{i}'
                i += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('products:detail', kwargs={'slug': self.slug})

    @property
    def en_stock(self):
        return self.disponible and self.quantite_stock > 0

    @property
    def note_moyenne(self):
        """Average rating, or None when the product has no review yet."""
        result = self.avis.aggregate(moyenne=Avg('note'))['moyenne']
        return round(result, 1) if result is not None else None

    @property
    def nombre_avis(self):
        return self.avis.count()


class Avis(models.Model):
    """A rating + comment left by a client on a product."""

    NOTE_CHOICES = [(i, f'{i} / 5') for i in range(1, 6)]

    produit = models.ForeignKey(Produit, on_delete=models.CASCADE, related_name='avis')
    utilisateur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='avis',
    )
    note = models.PositiveSmallIntegerField('note', choices=NOTE_CHOICES, default=5)
    commentaire = models.TextField('commentaire', blank=True)
    cree_le = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'avis'
        verbose_name = 'Avis'
        verbose_name_plural = 'Avis'
        ordering = ['-cree_le']
        unique_together = ['produit', 'utilisateur']

    def __str__(self):
        return f'{self.utilisateur.get_short_name()} — {self.note}/5 sur {self.produit.nom}'
