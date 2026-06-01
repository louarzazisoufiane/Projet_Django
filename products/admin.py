from django.contrib import admin

from .models import Avis, Categorie, Produit


@admin.register(Categorie)
class CategorieAdmin(admin.ModelAdmin):
    list_display = ('nom', 'slug', 'nombre_produits', 'cree_le')
    search_fields = ('nom',)
    prepopulated_fields = {'slug': ('nom',)}

    @admin.display(description='Produits')
    def nombre_produits(self, obj):
        return obj.produits.count()


class AvisInline(admin.TabularInline):
    model = Avis
    extra = 0
    readonly_fields = ('utilisateur', 'note', 'commentaire', 'cree_le')
    can_delete = True


@admin.register(Produit)
class ProduitAdmin(admin.ModelAdmin):
    list_display = ('nom', 'categorie', 'prix', 'quantite_stock', 'disponible', 'date_ajout')
    list_filter = ('disponible', 'categorie')
    list_editable = ('prix', 'quantite_stock', 'disponible')
    search_fields = ('nom', 'description')
    prepopulated_fields = {'slug': ('nom',)}
    inlines = [AvisInline]
    date_hierarchy = 'date_ajout'


@admin.register(Avis)
class AvisAdmin(admin.ModelAdmin):
    list_display = ('produit', 'utilisateur', 'note', 'cree_le')
    list_filter = ('note',)
    search_fields = ('produit__nom', 'utilisateur__email')
