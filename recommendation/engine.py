"""
Content-based product recommendation engine.

Approach (see section 7 of the specification):
  * each product is represented by a text built from its name, category
    and description;
  * TF-IDF turns those texts into vectors;
  * cosine similarity measures how close two products are;
  * the most similar products (boosted when they share the category /
    a close price) are returned.

scikit-learn is used for the TF-IDF + cosine-similarity computation.
"""
from __future__ import annotations

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# A small French stop-word list — keeps the dependency footprint light.
STOP_WORDS = [
    'le', 'la', 'les', 'un', 'une', 'des', 'de', 'du', 'et', 'ou', 'a', 'à',
    'au', 'aux', 'en', 'pour', 'par', 'avec', 'sur', 'dans', 'ce', 'cette',
    'ces', 'son', 'sa', 'ses', 'votre', 'vos', 'qui', 'que', 'est', 'plus',
]


def _document(produit) -> str:
    """Build the textual representation of a product."""
    categorie = produit.categorie.nom if produit.categorie_id else ''
    # The category is repeated so it weighs more in the similarity.
    return f'{produit.nom} {categorie} {categorie} {produit.description}'.lower()


def produits_similaires(produit, limite: int = 4):
    """
    Return up to `limite` products similar to `produit`.

    Falls back to other products of the same category (then any product)
    when there is not enough textual data to compute a similarity.
    """
    from products.models import Produit

    candidats = list(
        Produit.objects.filter(disponible=True)
        .exclude(pk=produit.pk)
        .select_related('categorie')
    )
    if not candidats:
        return []

    corpus = [_document(produit)] + [_document(p) for p in candidats]

    try:
        vectorizer = TfidfVectorizer(stop_words=STOP_WORDS, min_df=1)
        matrice = vectorizer.fit_transform(corpus)
        scores = cosine_similarity(matrice[0:1], matrice[1:]).flatten()
    except ValueError:
        # Empty vocabulary (all descriptions empty) -> fall back below.
        scores = [0.0] * len(candidats)

    # Combine textual similarity with a small same-category bonus.
    classes = []
    for candidat, score in zip(candidats, scores):
        bonus = 0.15 if candidat.categorie_id == produit.categorie_id else 0.0
        classes.append((candidat, float(score) + bonus))

    classes.sort(key=lambda item: item[1], reverse=True)
    resultats = [c for c, s in classes if s > 0][:limite]

    # Final fallback: just return same-category / latest products.
    if not resultats:
        resultats = [c for c, _ in classes][:limite]
    return resultats
