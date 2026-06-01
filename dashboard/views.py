"""
Management dashboard (administrateur / gestionnaire).

Provides the statistics required by section 6.7 and simple management of
products, categories, orders, clients and stock.
"""
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.db.models import Count, DecimalField, F, Sum
from django.db.models.functions import Coalesce
from django.shortcuts import get_object_or_404, redirect, render

from accounts.decorators import gestionnaire_required
from orders.models import Commande, LigneCommande
from products.models import Categorie, Produit

Utilisateur = get_user_model()

# Orders in these statuses count toward revenue.
STATUTS_VALIDES = [
    Commande.Statut.CONFIRMEE,
    Commande.Statut.EN_PREPARATION,
    Commande.Statut.EXPEDIEE,
    Commande.Statut.LIVREE,
]


@gestionnaire_required
def accueil(request):
    """Main dashboard with key statistics."""
    chiffre_affaires = (
        Commande.objects.filter(statut__in=STATUTS_VALIDES)
        .aggregate(total=Coalesce(Sum('montant_total'),
                                  0, output_field=DecimalField()))['total']
    )

    # Best-selling products (by quantity ordered).
    produits_populaires = (
        LigneCommande.objects
        .values('nom_produit')
        .annotate(quantite_vendue=Sum('quantite'))
        .order_by('-quantite_vendue')[:5]
    )

    # Orders grouped by status.
    commandes_par_statut = {
        statut.label: 0 for statut in Commande.Statut
    }
    for row in Commande.objects.values('statut').annotate(n=Count('id')):
        label = Commande.Statut(row['statut']).label
        commandes_par_statut[label] = row['n']

    context = {
        'nb_produits': Produit.objects.count(),
        'nb_clients': Utilisateur.objects.filter(role=Utilisateur.Role.CLIENT).count(),
        'nb_commandes': Commande.objects.count(),
        'chiffre_affaires': chiffre_affaires,
        'produits_populaires': produits_populaires,
        'commandes_recentes': Commande.objects.select_related('client')[:8],
        'commandes_par_statut': commandes_par_statut,
        'stock_faible': Produit.objects.filter(quantite_stock__lte=5).order_by('quantite_stock')[:8],
    }
    return render(request, 'dashboard/accueil.html', context)


@gestionnaire_required
def liste_commandes(request):
    commandes = Commande.objects.select_related('client').all()
    statut = request.GET.get('statut')
    if statut:
        commandes = commandes.filter(statut=statut)
    return render(request, 'dashboard/commandes.html', {
        'commandes': commandes,
        'statuts': Commande.Statut.choices,
        'statut_actif': statut,
    })


@gestionnaire_required
def changer_statut(request, pk):
    commande = get_object_or_404(Commande, pk=pk)
    if request.method == 'POST':
        nouveau = request.POST.get('statut')
        if nouveau in Commande.Statut.values:
            commande.statut = nouveau
            commande.save(update_fields=['statut'])
            messages.success(request, f'Statut de la commande #{commande.pk} mis à jour.')
    return redirect('dashboard:commandes')


@gestionnaire_required
def liste_clients(request):
    clients = (
        Utilisateur.objects.filter(role=Utilisateur.Role.CLIENT)
        .annotate(nb_commandes=Count('commandes'))
        .order_by('-date_joined')
    )
    return render(request, 'dashboard/clients.html', {'clients': clients})


@gestionnaire_required
def liste_produits(request):
    produits = Produit.objects.select_related('categorie').all()
    return render(request, 'dashboard/produits.html', {
        'produits': produits,
        'categories': Categorie.objects.all(),
    })
