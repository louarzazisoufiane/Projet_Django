"""Storefront views: home page, catalogue and product detail."""
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from recommendation.engine import produits_similaires

from .forms import AvisForm
from .models import Categorie, Produit

# Allowed ordering options exposed in the UI -> ORM field.
TRIS = {
    'recent': '-date_ajout',
    'ancien': 'date_ajout',
    'prix_asc': 'prix',
    'prix_desc': '-prix',
    'nom': 'nom',
}


def home(request):
    """Landing page with featured / latest products."""
    produits = (Produit.objects.filter(disponible=True)
                .select_related('categorie')[:8])
    categories = Categorie.objects.all()[:6]
    return render(request, 'products/home.html', {
        'produits': produits,
        'categories': categories,
    })


def catalogue(request):
    """Product grid with keyword search, category filter and sorting."""
    produits = Produit.objects.select_related('categorie')

    # Visitors only see available products; managers can see everything.
    if not (request.user.is_authenticated and request.user.is_gestionnaire):
        produits = produits.filter(disponible=True)
    elif request.GET.get('stock') == 'disponibles':
        produits = produits.filter(disponible=True)

    recherche = request.GET.get('q', '').strip()
    if recherche:
        produits = produits.filter(
            Q(nom__icontains=recherche) | Q(description__icontains=recherche)
        )

    categorie_slug = request.GET.get('categorie', '').strip()
    categorie_active = None
    if categorie_slug:
        categorie_active = Categorie.objects.filter(slug=categorie_slug).first()
        if categorie_active:
            produits = produits.filter(categorie=categorie_active)

    tri = request.GET.get('tri', 'recent')
    produits = produits.order_by(TRIS.get(tri, '-date_ajout'))

    paginator = Paginator(produits, 12)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'products/catalogue.html', {
        'page_obj': page_obj,
        'categories': Categorie.objects.all(),
        'recherche': recherche,
        'categorie_active': categorie_active,
        'tri': tri,
    })


def detail(request, slug):
    """Product detail page with reviews and similar-product recommendations."""
    produit = get_object_or_404(Produit.objects.select_related('categorie'), slug=slug)
    avis = produit.avis.select_related('utilisateur')

    # A connected client may post / update a single review per product.
    avis_utilisateur = None
    if request.user.is_authenticated:
        avis_utilisateur = avis.filter(utilisateur=request.user).first()

    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.warning(request, 'Connectez-vous pour laisser un avis.')
            return redirect('accounts:login')
        form = AvisForm(request.POST, instance=avis_utilisateur)
        if form.is_valid():
            avis_obj = form.save(commit=False)
            avis_obj.produit = produit
            avis_obj.utilisateur = request.user
            avis_obj.save()
            messages.success(request, 'Merci, votre avis a été enregistré.')
            return redirect(produit.get_absolute_url())
    else:
        form = AvisForm(instance=avis_utilisateur)

    return render(request, 'products/detail.html', {
        'produit': produit,
        'avis': avis,
        'form': form,
        'avis_utilisateur': avis_utilisateur,
        'recommandations': produits_similaires(produit, limite=4),
    })


@login_required
def supprimer_avis(request, pk):
    """Let a client delete their own review."""
    from .models import Avis
    avis = get_object_or_404(Avis, pk=pk, utilisateur=request.user)
    produit = avis.produit
    if request.method == 'POST':
        avis.delete()
        messages.info(request, 'Votre avis a été supprimé.')
    return redirect(produit.get_absolute_url())
