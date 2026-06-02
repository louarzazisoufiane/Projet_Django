"""
Validation des fichiers téléversés (§12 — « les fichiers uploadés doivent être
contrôlés »).

Limite la taille et restreint les extensions/types des images de produits et de
catégories afin d'éviter le dépôt de fichiers volumineux ou non conformes.
"""
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.template.defaultfilters import filesizeformat

# Taille maximale d'une image téléversée (5 Mo).
TAILLE_MAX_IMAGE = 5 * 1024 * 1024

# Extensions d'image autorisées.
EXTENSIONS_IMAGE_AUTORISEES = ['jpg', 'jpeg', 'png', 'webp', 'gif']

# Réutilisable comme validateur d'extension sur un ImageField.
valider_extension_image = FileExtensionValidator(
    allowed_extensions=EXTENSIONS_IMAGE_AUTORISEES,
)


def valider_taille_image(fichier):
    """Rejette les images dépassant ``TAILLE_MAX_IMAGE``."""
    if fichier and fichier.size > TAILLE_MAX_IMAGE:
        raise ValidationError(
            "L'image est trop volumineuse (%(taille)s). "
            "Taille maximale autorisée : %(max)s." % {
                'taille': filesizeformat(fichier.size),
                'max': filesizeformat(TAILLE_MAX_IMAGE),
            }
        )
