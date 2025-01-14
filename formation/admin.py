from django.contrib import admin

from .models import Categorie, SousCategorie, Formation, Chapitre, Video, Cour, VideoVue, Temoignage, \
    Discution, SeanceTravail, Suive


# Register your models here.


@admin.register(Categorie)
class CategorieAdmin(admin.ModelAdmin):
    ...


@admin.register(SousCategorie)
class SousCategorieAdmin(admin.ModelAdmin):
    ...


@admin.register(Formation)
class FormationAdmin(admin.ModelAdmin):
    ...


@admin.register(Chapitre)
class ChapitreAdmin(admin.ModelAdmin):
    ...


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    ...


@admin.register(Cour)
class CourAdmin(admin.ModelAdmin):
    ...


@admin.register(Suive)
class SuiveAdmin(admin.ModelAdmin):
    ...


@admin.register(VideoVue)
class VideoVueAdmin(admin.ModelAdmin):
    ...


@admin.register(Temoignage)
class TemoignageAdmin(admin.ModelAdmin):
    ...


@admin.register(Discution)
class DiscutionAdmin(admin.ModelAdmin):
    ...


@admin.register(SeanceTravail)
class SeanceTravailAdmin(admin.ModelAdmin):
    ...
