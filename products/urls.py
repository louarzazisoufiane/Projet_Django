from django.urls import path

from . import views

app_name = 'products'

urlpatterns = [
    path('', views.home, name='home'),
    path('catalogue/', views.catalogue, name='catalogue'),
    path('produit/<slug:slug>/', views.detail, name='detail'),
    path('avis/<int:pk>/supprimer/', views.supprimer_avis, name='supprimer_avis'),
]
