"""Make a lightweight cart summary available in the navbar."""


def cart_summary(request):
    count = 0
    if request.user.is_authenticated:
        panier = getattr(request.user, 'panier', None)
        if panier is not None:
            count = panier.nombre_articles
    return {'panier_count': count}
