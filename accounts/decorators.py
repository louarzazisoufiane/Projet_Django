"""Reusable access-control helpers."""
from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied


def gestionnaire_required(view_func):
    """Allow access only to managers / administrators."""

    @wraps(view_func)
    @login_required
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_gestionnaire:
            raise PermissionDenied("Accès réservé aux gestionnaires.")
        return view_func(request, *args, **kwargs)

    return _wrapped
