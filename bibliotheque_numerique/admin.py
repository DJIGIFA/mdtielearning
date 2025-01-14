from django.contrib import admin

from .models import Categorie, Auteur, Livre


# Register your models here.

@admin.register(Categorie)
class CategorieAdmin(admin.ModelAdmin):
    ...


@admin.register(Auteur)
class AuteurAdmin(admin.ModelAdmin):
    ...


@admin.register(Livre)
class LivreAdmin(admin.ModelAdmin):
    ...
