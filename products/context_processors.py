"""Expose the category list to every template (used by the navbar)."""
from .models import Categorie


def categories(request):
    return {'nav_categories': Categorie.objects.all()}
