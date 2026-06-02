"""
Root URL configuration for the E-Shop Django platform.
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.views.static import serve

urlpatterns = [
    path('django-admin/', admin.site.urls),
    path('', include('products.urls')),
    path('accounts/', include('accounts.urls')),
    path('cart/', include('cart.urls')),
    path('orders/', include('orders.urls')),
    path('dashboard/', include('dashboard.urls')),
]

# Sert les fichiers médias téléversés directement par Django.
# Les fichiers statiques sont servis par WhiteNoise (middleware) ; les médias
# (images produits, etc.) le sont ici, y compris en production où il n'y a pas
# de serveur web dédié (nginx) devant l'application.
urlpatterns += [
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]

admin.site.site_header = 'E-Shop Django — Administration'
admin.site.site_title = 'E-Shop Django'
admin.site.index_title = 'Gestion de la plateforme'
