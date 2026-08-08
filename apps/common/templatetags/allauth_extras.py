"""Petits utilitaires pour restyler les templates par défaut de django-allauth
(voir templates/allauth/) sans dupliquer toute sa logique."""
from django import template

register = template.Library()


@register.filter
def has_tag(tags, name):
    """True si `name` est présent dans la liste `tags` passée par les
    templates allauth via `{% element button tags="outline,cancel" %}`.
    Gère proprement le cas où `tags` est None (aucun tag fourni)."""
    return bool(tags) and name in tags
