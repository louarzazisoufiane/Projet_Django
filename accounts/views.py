"""Authentication and profile views."""
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect, render
from django.urls import reverse_lazy

from .forms import (
    ConnexionForm,
    InscriptionForm,
    ProfilClientForm,
    UtilisateurForm,
)


def inscription(request):
    """Create a new client account and log the user in."""
    if request.user.is_authenticated:
        return redirect('products:home')

    if request.method == 'POST':
        form = InscriptionForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user, backend='accounts.backends.EmailBackend')
            messages.success(request, 'Votre compte a été créé avec succès. Bienvenue !')
            return redirect('products:home')
    else:
        form = InscriptionForm()
    return render(request, 'accounts/inscription.html', {'form': form})


class ConnexionView(LoginView):
    template_name = 'accounts/connexion.html'
    authentication_form = ConnexionForm
    redirect_authenticated_user = True

    def form_valid(self, form):
        messages.success(self.request, 'Connexion réussie.')
        return super().form_valid(form)


@login_required
def deconnexion(request):
    logout(request)
    messages.info(request, 'Vous avez été déconnecté.')
    return redirect('products:home')


@login_required
def profil(request):
    """Display and update the connected user's account and profile."""
    profil_client = request.user.profil
    if request.method == 'POST':
        user_form = UtilisateurForm(request.POST, instance=request.user)
        profil_form = ProfilClientForm(request.POST, instance=profil_client)
        if user_form.is_valid() and profil_form.is_valid():
            user_form.save()
            profil_form.save()
            messages.success(request, 'Votre profil a été mis à jour.')
            return redirect('accounts:profil')
    else:
        user_form = UtilisateurForm(instance=request.user)
        profil_form = ProfilClientForm(instance=profil_client)

    return render(request, 'accounts/profil.html', {
        'user_form': user_form,
        'profil_form': profil_form,
    })
