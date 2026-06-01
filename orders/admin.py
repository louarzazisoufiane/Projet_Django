from django.contrib import admin

from .models import Commande, LigneCommande


class LigneCommandeInline(admin.TabularInline):
    model = LigneCommande
    extra = 0
    readonly_fields = ('produit', 'nom_produit', 'prix_unitaire', 'quantite', 'sous_total')

    @admin.display(description='Sous-total')
    def sous_total(self, obj):
        return obj.sous_total


@admin.register(Commande)
class CommandeAdmin(admin.ModelAdmin):
    list_display = ('id', 'client', 'statut', 'montant_total', 'nombre_articles', 'date_commande')
    list_filter = ('statut', 'date_commande')
    list_editable = ('statut',)
    search_fields = ('client__email', 'nom_complet', 'ville')
    date_hierarchy = 'date_commande'
    inlines = [LigneCommandeInline]
    readonly_fields = ('montant_total', 'date_commande', 'modifie_le')
