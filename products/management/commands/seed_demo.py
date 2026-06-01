"""Populate the database with demo categories, products and an admin account."""
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from products.models import Categorie, Produit

Utilisateur = get_user_model()

CATEGORIES = {
    'Ordinateurs': [
        ('Ordinateur portable Pro 15"', '7999.00', 12,
         "Ordinateur portable léger et puissant, idéal pour le travail et la bureautique."),
        ('Ordinateur de bureau Gamer', '11999.00', 6,
         "Ordinateur de bureau performant pour les jeux et le montage vidéo."),
        ('Souris sans fil ergonomique', '199.00', 50,
         "Souris sans fil confortable et précise pour votre ordinateur."),
        ('Clavier mécanique rétroéclairé', '499.00', 30,
         "Clavier mécanique réactif avec rétroéclairage pour ordinateur."),
        ('Sac à dos pour PC portable', '349.00', 25,
         "Sac à dos résistant pour transporter votre ordinateur portable en sécurité."),
    ],
    'Livres': [
        ('Apprendre Django facilement', '250.00', 40,
         "Un livre complet pour apprendre le développement web avec Django."),
        ('Python pour les débutants', '220.00', 35,
         "Un livre d'introduction à la programmation avec le langage Python."),
        ('Algorithmes et structures de données', '300.00', 20,
         "Un livre de référence sur les algorithmes et les structures de données."),
    ],
    'Vêtements': [
        ('T-shirt coton bio', '149.00', 60,
         "T-shirt en coton biologique confortable, disponible en plusieurs tailles."),
        ('Veste légère imperméable', '599.00', 18,
         "Veste légère et imperméable, parfaite pour les sorties en ville."),
    ],
}


class Command(BaseCommand):
    help = "Crée des données de démonstration (catégories, produits, admin)."

    def handle(self, *args, **options):
        admin_email = 'admin@example.com'
        if not Utilisateur.objects.filter(email=admin_email).exists():
            Utilisateur.objects.create_superuser(
                email=admin_email, password='admin12345',
                first_name='Admin', last_name='Démo',
            )
            self.stdout.write(self.style.SUCCESS(
                f'Compte administrateur créé : {admin_email} / admin12345'))

        for nom_cat, produits in CATEGORIES.items():
            categorie, _ = Categorie.objects.get_or_create(nom=nom_cat)
            for nom, prix, stock, desc in produits:
                Produit.objects.get_or_create(
                    nom=nom,
                    defaults={
                        'prix': Decimal(prix),
                        'quantite_stock': stock,
                        'disponible': stock > 0,
                        'description': desc,
                        'categorie': categorie,
                    },
                )
        self.stdout.write(self.style.SUCCESS('Données de démonstration créées.'))
