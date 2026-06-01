from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import ProfilClient, Utilisateur


class ProfilClientInline(admin.StackedInline):
    model = ProfilClient
    can_delete = False
    extra = 0


@admin.register(Utilisateur)
class UtilisateurAdmin(UserAdmin):
    model = Utilisateur
    inlines = [ProfilClientInline]
    list_display = ('email', 'first_name', 'last_name', 'role', 'is_active', 'date_joined')
    list_filter = ('role', 'is_active', 'is_staff')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('-date_joined',)

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Informations personnelles', {'fields': ('first_name', 'last_name')}),
        ('Rôle et permissions', {
            'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Dates', {'fields': ('last_login', 'date_joined')}),
    )
    readonly_fields = ('date_joined', 'last_login')
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'role', 'password1', 'password2'),
        }),
    )


@admin.register(ProfilClient)
class ProfilClientAdmin(admin.ModelAdmin):
    list_display = ('utilisateur', 'telephone', 'ville', 'pays')
    search_fields = ('utilisateur__email', 'ville')
