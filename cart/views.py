"""Cart management: view, add, update quantity, remove, clear."""
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from products.models import Produit

from .models import LignePanier, Panier


def _get_panier(user):
    panier, _ = Panier.objects.get_or_create(utilisateur=user)
    return panier


@login_required
def detail_panier(request):
    panier = _get_panier(request.user)
    lignes = panier.lignes.select_related('produit', 'produit__categorie')
    return render(request, 'cart/panier.html', {'panier': panier, 'lignes': lignes})


@login_required
@require_POST
def ajouter(request, produit_id):
    produit = get_object_or_404(Produit, pk=produit_id, disponible=True)
    quantite = max(1, int(request.POST.get('quantite', 1) or 1))
    panier = _get_panier(request.user)

    ligne, created = LignePanier.objects.get_or_create(
        panier=panier, produit=produit,
        defaults={'quantite': quantite},
    )
    if not created:
        ligne.quantite += quantite

    # Never exceed available stock.
    if ligne.quantite > produit.quantite_stock:
        ligne.quantite = produit.quantite_stock or 1
        messages.warning(request, f'Stock limité : quantité ajustée à {ligne.quantite}.')
    ligne.save()

    messages.success(request, f'« {produit.nom} » a été ajouté au panier.')
    return redirect(request.POST.get('next') or 'cart:detail')


@login_required
@require_POST
def modifier(request, ligne_id):
    ligne = get_object_or_404(LignePanier, pk=ligne_id, panier__utilisateur=request.user)
    quantite = int(request.POST.get('quantite', 1) or 1)
    if quantite <= 0:
        ligne.delete()
        messages.info(request, 'Article retiré du panier.')
    else:
        if quantite > ligne.produit.quantite_stock:
            quantite = ligne.produit.quantite_stock or 1
            messages.warning(request, f'Stock limité : quantité ajustée à {quantite}.')
        ligne.quantite = quantite
        ligne.save()
    return redirect('cart:detail')


@login_required
@require_POST
def supprimer(request, ligne_id):
    ligne = get_object_or_404(LignePanier, pk=ligne_id, panier__utilisateur=request.user)
    ligne.delete()
    messages.info(request, 'Article retiré du panier.')
    return redirect('cart:detail')


@login_required
@require_POST
def vider(request):
    panier = _get_panier(request.user)
    panier.lignes.all().delete()
    messages.info(request, 'Votre panier a été vidé.')
    return redirect('cart:detail')
