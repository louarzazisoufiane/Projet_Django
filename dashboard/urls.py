from django.urls import path

from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.accueil, name='accueil'),
    path('commandes/', views.liste_commandes, name='commandes'),
    path('commandes/<int:pk>/statut/', views.changer_statut, name='changer_statut'),
    path('clients/', views.liste_clients, name='clients'),
    path('produits/', views.liste_produits, name='produits'),
]
