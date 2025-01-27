from django.db import models
from django.utils.text import slugify

from utilisateur.models import Utilisateur


# Create your models here.

class Categorie(models.Model):
    nom = models.CharField(max_length=200)
    image = models.ImageField()
    description = models.TextField(null=True, blank=True)
    slug = models.SlugField()

    date = models.DateField(auto_now_add=True)

    @property
    def all_livre(self):
        return self.livre_set.all()

    def _get_unique_slug(self):
        slug = slugify(self.nom)
        unique_slug = slug
        num = 1
        while Categorie.objects.filter(slug=unique_slug).exists():
            unique_slug = "{}-{}".format(slug, num)
            num += 1
        return unique_slug

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self._get_unique_slug()
        super().save()


class Auteur(models.Model):
    admin = models.ForeignKey(Utilisateur, on_delete=models.CASCADE)
    nom = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    date = models.DateField(auto_now_add=True)
    slug = models.SlugField()

    def _get_unique_slug(self):
        slug = slugify(self.nom)
        unique_slug = slug
        num = 1
        while Categorie.objects.filter(slug=unique_slug).exists():
            unique_slug = "{}-{}".format(slug, num)
            num += 1
        return unique_slug

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self._get_unique_slug()
        super().save()


class Livre(models.Model):

    nom = models.CharField(max_length=200)
    reference = models.CharField(max_length=200)
    image = models.ImageField()
    description = models.TextField(null=True, blank=True)
    slug = models.SlugField()

    document = models.FileField()

    date = models.DateField(auto_now_add=True)

    admin = models.ForeignKey(Utilisateur, on_delete=models.CASCADE)
    auteur = models.ForeignKey(Auteur, on_delete=models.CASCADE)
    categorie = models.ForeignKey(Categorie, on_delete=models.CASCADE)

    def _get_unique_slug(self):
        slug = slugify(self.nom)
        unique_slug = slug
        num = 1
        while Categorie.objects.filter(slug=unique_slug).exists():
            unique_slug = "{}-{}".format(slug, num)
            num += 1
        return unique_slug

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self._get_unique_slug()
        super().save()

