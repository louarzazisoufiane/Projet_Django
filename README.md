# E-Shop Django

Plateforme e-commerce développée avec **Django** dans le cadre du projet de fin de
module *Développement Web avec Django*. Application web complète, rendue côté
serveur avec les **Django Templates** et **Bootstrap 5**, intégrant la gestion des
utilisateurs, des produits, du panier, des commandes, un tableau de bord
d'administration, une **fonctionnalité d'intelligence artificielle** (recommandation
de produits), la conteneurisation Docker et une pipeline CI/CD GitHub Actions.

## Architecture

```
django_ecommerce/
├── ecommerce/          # configuration du projet (settings, urls, wsgi/asgi)
├── accounts/           # utilisateurs, inscription, connexion, profils
├── products/           # produits, catégories, recherche, filtres, avis
├── cart/               # gestion du panier
├── orders/             # gestion des commandes
├── dashboard/          # statistiques et administration
├── recommendation/     # fonctionnalité IA de recommandation (TF-IDF + cosinus)
├── templates/          # gabarits Django (Bootstrap 5)
├── static/             # fichiers statiques (CSS, JS, images)
├── media/              # fichiers médias téléversés
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env.example
└── .github/workflows/ci-cd.yml
```

## Acteurs

- **Visiteur** : consulte l'accueil, le catalogue, recherche/filtre les produits, crée un compte.
- **Client** : se connecte, gère son profil, son panier, passe et suit ses commandes, laisse des avis.
- **Administrateur / Gestionnaire** : gère produits, catégories, stocks, commandes, clients et statistiques.

## Fonctionnalité IA — recommandation de produits

Sur la page d'un produit, des **produits similaires** sont proposés automatiquement.
La similarité est calculée avec **TF-IDF** (sur le nom, la catégorie et la description)
et la **similarité cosinus** via **scikit-learn** (voir `recommendation/engine.py`).

## Démarrage rapide (développement local, SQLite)

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

cp .env.example .env          # optionnel : par défaut SQLite est utilisé
python manage.py migrate
python manage.py seed_demo     # données de démo + admin (admin@example.com / admin12345)
python manage.py runserver
```

Application : http://127.0.0.1:8000 — Administration : http://127.0.0.1:8000/django-admin/

> Sans variable `DB_NAME`, le projet utilise SQLite automatiquement. Renseignez les
> variables `DB_*` dans `.env` pour utiliser PostgreSQL.

## Déploiement avec Docker Compose (PostgreSQL + Gunicorn + Nginx)

```bash
cp .env.example .env          # renseignez SECRET_KEY, DEBUG=False, DB_*, POSTGRES_*
docker compose up --build
```

L'application est servie par Nginx sur http://localhost (port 80). Le conteneur web
applique les migrations, collecte les fichiers statiques et crée le compte
administrateur défini par `DJANGO_SUPERUSER_EMAIL` / `DJANGO_SUPERUSER_PASSWORD`.

## Variables d'environnement

Voir `.env.example`. Les informations sensibles (`SECRET_KEY`, mots de passe) ne
doivent jamais être committées : le fichier `.env` est ignoré par Git.

## Tests

```bash
python manage.py test
```

## Sécurité

- Authentification obligatoire pour passer une commande.
- Mots de passe gérés et hachés par le système d'authentification de Django.
- Protection CSRF activée, formulaires validés côté serveur.
- Espace d'administration et tableau de bord réservés aux gestionnaires
  (décorateur `gestionnaire_required` ; les clients reçoivent une page 403).
- `DEBUG=False`, cookies sécurisés et en-têtes de sécurité activés en production.
- Variables sensibles stockées dans `.env` (jamais publié).
- **Fichiers uploadés contrôlés** : extensions autorisées (`jpg/jpeg/png/webp/gif`)
  et taille limitée à 5 Mo (voir `products/validators.py`).
- **Gestion des erreurs** : pages `404`, `403` et `500` personnalisées et
  journalisation (`LOGGING` dans `settings.py`, niveau via `LOG_LEVEL`).

## Pipeline CI/CD

`.github/workflows/ci-cd.yml` : à chaque push sur `main`/`master`, GitHub Actions
exécute la pipeline suivante.

**Pipeline minimale (§11.1)**

1. récupération du code (`checkout`) ;
2. installation de Python 3.12 ;
3. installation des dépendances ;
4. migrations en environnement de test (PostgreSQL de service) ;
5. exécution des tests (`manage.py test`) ;
6. vérification de la qualité du code (`flake8`, config dans `setup.cfg`) ;
7. construction de l'image Docker ;
8. publication de l'image sur **Docker Hub**
   (`docker.io/<DOCKERHUB_USERNAME>/django-ecommerce`).

> **Secrets requis** (Settings → Secrets and variables → Actions) :
> `DOCKERHUB_USERNAME` (identifiant Docker Hub) et `DOCKERHUB_TOKEN`
> (jeton d'accès créé dans Docker Hub → Account Settings → Security).

**Pipeline avancée (§11.2)**

- scan de sécurité des dépendances (`pip-audit`) ;
- séparation des environnements (variables de test dédiées, jamais de prod) ;
- notification en cas d'échec de la pipeline (job `notify-failure`, webhook
  Slack/Discord à brancher).

> Le scan des dépendances est configuré en mode informatif. Pour le rendre
> bloquant : retirer `|| true` du `pip-audit`.
