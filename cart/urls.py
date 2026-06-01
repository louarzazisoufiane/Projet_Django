from django.urls import path

from . import views

app_name = 'cart'

urlpatterns = [
    path('', views.detail_panier, name='detail'),
    path('ajouter/<int:produit_id>/', views.ajouter, name='ajouter'),
    path('ligne/<int:ligne_id>/modifier/', views.modifier, name='modifier'),
    path('ligne/<int:ligne_id>/supprimer/', views.supprimer, name='supprimer'),
    path('vider/', views.vider, name='vider'),
]
