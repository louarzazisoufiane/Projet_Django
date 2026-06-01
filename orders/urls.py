from django.urls import path

from . import views

app_name = 'orders'

urlpatterns = [
    path('commander/', views.checkout, name='checkout'),
    path('mes-commandes/', views.mes_commandes, name='mes_commandes'),
    path('<int:pk>/', views.detail, name='detail'),
    path('<int:pk>/annuler/', views.annuler, name='annuler'),
]
