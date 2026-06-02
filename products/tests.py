"""Tests for the catalogue, reviews and recommendation engine."""
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from django.core.exceptions import ValidationError

from recommendation.engine import produits_similaires

from .models import Avis, Categorie, Produit
from .validators import TAILLE_MAX_IMAGE, valider_taille_image

Utilisateur = get_user_model()


class CatalogueTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.cat = Categorie.objects.create(nom='Informatique')
        cls.p1 = Produit.objects.create(
            nom='Ordinateur portable', prix=Decimal('5000'),
            categorie=cls.cat, quantite_stock=10, disponible=True,
            description='Un ordinateur portable puissant pour le travail.',
        )
        cls.p2 = Produit.objects.create(
            nom='Souris sans fil', prix=Decimal('150'),
            categorie=cls.cat, quantite_stock=0, disponible=False,
            description='Souris ergonomique sans fil pour ordinateur.',
        )

    def test_catalogue_hides_unavailable_products_from_visitors(self):
        response = self.client.get(reverse('products:catalogue'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Ordinateur portable')
        self.assertNotContains(response, 'Souris sans fil')

    def test_search_by_keyword(self):
        response = self.client.get(reverse('products:catalogue'), {'q': 'portable'})
        self.assertContains(response, 'Ordinateur portable')

    def test_filter_by_category(self):
        response = self.client.get(reverse('products:catalogue'), {'categorie': self.cat.slug})
        self.assertEqual(response.status_code, 200)

    def test_detail_page(self):
        response = self.client.get(self.p1.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Ordinateur portable')


class AvisTests(TestCase):
    def test_note_moyenne(self):
        cat = Categorie.objects.create(nom='Livres')
        produit = Produit.objects.create(nom='Livre Django', prix=Decimal('200'), categorie=cat)
        u1 = Utilisateur.objects.create_user('a@x.com', 'pass12345', first_name='A', last_name='A')
        u2 = Utilisateur.objects.create_user('b@x.com', 'pass12345', first_name='B', last_name='B')
        Avis.objects.create(produit=produit, utilisateur=u1, note=4)
        Avis.objects.create(produit=produit, utilisateur=u2, note=2)
        self.assertEqual(produit.note_moyenne, 3.0)
        self.assertEqual(produit.nombre_avis, 2)


class UploadValidationTests(TestCase):
    """§12 — les fichiers uploadés doivent être contrôlés."""

    class _FakeFile:
        def __init__(self, size):
            self.size = size

    def test_rejette_image_trop_volumineuse(self):
        with self.assertRaises(ValidationError):
            valider_taille_image(self._FakeFile(TAILLE_MAX_IMAGE + 1))

    def test_accepte_image_dans_la_limite(self):
        # Ne doit lever aucune exception.
        valider_taille_image(self._FakeFile(TAILLE_MAX_IMAGE))


class RecommendationTests(TestCase):
    def test_similar_products_share_theme(self):
        cat = Categorie.objects.create(nom='Informatique')
        base = Produit.objects.create(
            nom='Ordinateur portable', prix=Decimal('5000'), categorie=cat,
            description='ordinateur portable rapide pour le travail bureautique',
        )
        Produit.objects.create(
            nom='Ordinateur de bureau', prix=Decimal('4000'), categorie=cat,
            description='ordinateur de bureau rapide pour le travail',
        )
        Produit.objects.create(
            nom='Tapis de yoga', prix=Decimal('100'), categorie=cat,
            description='tapis confortable pour le sport et le yoga',
        )
        resultats = produits_similaires(base, limite=2)
        self.assertTrue(len(resultats) >= 1)
        self.assertNotIn(base, resultats)
