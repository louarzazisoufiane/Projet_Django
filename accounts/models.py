"""
User models.

`Utilisateur` is the custom user (clients, gestionnaires, administrateurs)
authenticated by email. `ProfilClient` holds the complementary information
of a client (phone, address...).
"""
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models


class UtilisateurManager(BaseUserManager):
    """Manager that uses the email address as the unique identifier."""

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("L'adresse e-mail est obligatoire.")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('role', Utilisateur.Role.ADMIN)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Un superutilisateur doit avoir is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Un superutilisateur doit avoir is_superuser=True.')
        return self.create_user(email, password, **extra_fields)


class Utilisateur(AbstractBaseUser, PermissionsMixin):
    """Represents a client, a gestionnaire or an administrateur."""

    class Role(models.TextChoices):
        CLIENT = 'CLIENT', 'Client'
        GESTIONNAIRE = 'GESTIONNAIRE', 'Gestionnaire'
        ADMIN = 'ADMIN', 'Administrateur'

    email = models.EmailField('adresse e-mail', unique=True, db_index=True)
    first_name = models.CharField('prénom', max_length=150)
    last_name = models.CharField('nom', max_length=150)
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.CLIENT)

    is_active = models.BooleanField('actif', default=True)
    is_staff = models.BooleanField('membre du staff', default=False)
    date_joined = models.DateTimeField("date d'inscription", auto_now_add=True)

    objects = UtilisateurManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    class Meta:
        db_table = 'utilisateurs'
        verbose_name = 'Utilisateur'
        verbose_name_plural = 'Utilisateurs'
        ordering = ['-date_joined']

    def __str__(self):
        return f'{self.get_full_name()} <{self.email}>'

    def get_full_name(self):
        full = f'{self.first_name} {self.last_name}'.strip()
        return full or self.email

    def get_short_name(self):
        return self.first_name or self.email

    @property
    def is_gestionnaire(self):
        """True for managers and admins (people who can manage the shop)."""
        return self.role in (self.Role.GESTIONNAIRE, self.Role.ADMIN) or self.is_staff

    def save(self, *args, **kwargs):
        # Managers/admins need staff access to reach the management area.
        if self.role in (self.Role.GESTIONNAIRE, self.Role.ADMIN):
            self.is_staff = True
        super().save(*args, **kwargs)


class ProfilClient(models.Model):
    """Complementary information attached to a client account."""

    utilisateur = models.OneToOneField(
        Utilisateur,
        on_delete=models.CASCADE,
        related_name='profil',
    )
    telephone = models.CharField('téléphone', max_length=30, blank=True)
    adresse = models.CharField('adresse', max_length=255, blank=True)
    ville = models.CharField('ville', max_length=120, blank=True)
    code_postal = models.CharField('code postal', max_length=20, blank=True)
    pays = models.CharField('pays', max_length=100, blank=True, default='Maroc')
    cree_le = models.DateTimeField(auto_now_add=True)
    modifie_le = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'profils_clients'
        verbose_name = 'Profil client'
        verbose_name_plural = 'Profils clients'

    def __str__(self):
        return f'Profil de {self.utilisateur.get_full_name()}'
