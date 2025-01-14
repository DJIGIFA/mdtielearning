from django.db import models

from root.outil import MOYEN_PAIEMENT
from utilisateur.models import Utilisateur


# Create your models here.


class Type(models.Model):
    nom = models.CharField(max_length=255)


class Niveau(models.Model):
    nom = models.CharField(max_length=255)


class Matiere(models.Model):
    nom = models.CharField(max_length=255)


class Pays(models.Model):
    nom = models.CharField(max_length=255)


class Document(models.Model):
    type = models.ForeignKey(Type, on_delete=models.CASCADE)
    niveau = models.ForeignKey(Niveau, on_delete=models.CASCADE)
    pays = models.ForeignKey(Pays, on_delete=models.CASCADE)
    matiere = models.ForeignKey(Matiere, on_delete=models.CASCADE)

    nom = models.CharField(max_length=255)
    annee = models.CharField(max_length=255)

    document = models.FileField()

    prix = models.IntegerField()
    miniature = models.ImageField()
    date = models.DateField(auto_now_add=True)


class DocumentAcheter(models.Model):
    document = models.ForeignKey(Document, on_delete=models.CASCADE)
    apprenant = models.ForeignKey(Utilisateur, on_delete=models.CASCADE)

    montant = models.FloatField()
    date = models.DateTimeField(auto_now_add=True)


# gestion du paiement


class PaiementDocument(models.Model):
    order_id = models.CharField(max_length=512, unique=True)
    payer = models.BooleanField(default=False)

    moyen_paiement = models.CharField(max_length=50, choices=MOYEN_PAIEMENT)

    date_soumission = models.DateTimeField(auto_now_add=True)
    date_validation = models.DateTimeField(null=True)

    montant = models.FloatField()
    document = models.ForeignKey(Document, on_delete=models.CASCADE)
    client = models.ForeignKey(Utilisateur, on_delete=models.CASCADE)

    numero = models.CharField(max_length=30, null=True)

    strip_link = models.URLField(null=True)
