from django.contrib import admin

from .models import LignePanier, Panier


class LignePanierInline(admin.TabularInline):
    model = LignePanier
    extra = 0


@admin.register(Panier)
class PanierAdmin(admin.ModelAdmin):
    list_display = ('utilisateur', 'nombre_articles', 'montant_total', 'modifie_le')
    inlines = [LignePanierInline]
