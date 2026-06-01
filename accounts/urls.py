from django.urls import path

from . import views

app_name = 'accounts'

urlpatterns = [
    path('inscription/', views.inscription, name='inscription'),
    path('connexion/', views.ConnexionView.as_view(), name='login'),
    path('deconnexion/', views.deconnexion, name='logout'),
    path('profil/', views.profil, name='profil'),
]
