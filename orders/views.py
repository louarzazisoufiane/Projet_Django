"""Checkout and order history for clients."""
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render

from cart.models import Panier

from .forms import CheckoutForm
from .models import Commande, LigneCommande


@login_required
def checkout(request):
    """Validate the cart into an order (authentication required — §12)."""
    panier = Panier.objects.filter(utilisateur=request.user).first()
    lignes = panier.lignes.select_related('produit') if panier else []

    if not lignes:
        messages.warning(request, 'Votre panier est vide.')
        return redirect('cart:detail')

    # Pre-fill the form from the client's profile.
    profil = getattr(request.user, 'profil', None)
    initial = {'nom_complet': request.user.get_full_name()}
    if profil:
        initial.update({
            'telephone': profil.telephone,
            'adresse': profil.adresse,
            'ville': profil.ville,
            'code_postal': profil.code_postal,
        })

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            commande = _creer_commande(request.user, panier, form)
            messages.success(request, f'Votre commande #{commande.pk} a été enregistrée.')
            return redirect('orders:detail', pk=commande.pk)
    else:
        form = CheckoutForm(initial=initial)

    return render(request, 'orders/checkout.html', {
        'form': form,
        'panier': panier,
        'lignes': lignes,
    })


@transaction.atomic
def _creer_commande(utilisateur, panier, form):
    """Create the order, copy cart lines, decrement stock and clear the cart."""
    commande = form.save(commit=False)
    commande.client = utilisateur
    commande.statut = Commande.Statut.EN_ATTENTE
    commande.save()

    for ligne in panier.lignes.select_related('produit'):
        produit = ligne.produit
        LigneCommande.objects.create(
            commande=commande,
            produit=produit,
            nom_produit=produit.nom,
            prix_unitaire=produit.prix,
            quantite=ligne.quantite,
        )
        # Decrement stock and update availability.
        produit.quantite_stock = max(0, produit.quantite_stock - ligne.quantite)
        if produit.quantite_stock == 0:
            produit.disponible = False
        produit.save(update_fields=['quantite_stock', 'disponible'])

    commande.recalculer_total()
    commande.save(update_fields=['montant_total'])
    panier.lignes.all().delete()
    return commande


@login_required
def mes_commandes(request):
    commandes = (Commande.objects.filter(client=request.user)
                 .prefetch_related('lignes'))
    return render(request, 'orders/mes_commandes.html', {'commandes': commandes})


@login_required
def detail(request, pk):
    commande = get_object_or_404(
        Commande.objects.prefetch_related('lignes'),
        pk=pk, client=request.user,
    )
    return render(request, 'orders/detail.html', {
        'commande': commande,
        'statuts': Commande.Statut.choices,
    })


@login_required
def annuler(request, pk):
    """Let a client cancel an order while it is still pending/confirmed."""
    commande = get_object_or_404(Commande, pk=pk, client=request.user)
    if request.method == 'POST':
        if commande.statut in (Commande.Statut.EN_ATTENTE, Commande.Statut.CONFIRMEE):
            commande.statut = Commande.Statut.ANNULEE
            commande.save(update_fields=['statut'])
            messages.info(request, f'La commande #{commande.pk} a été annulée.')
        else:
            messages.error(request, 'Cette commande ne peut plus être annulée.')
    return redirect('orders:detail', pk=commande.pk)
