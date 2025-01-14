from django.db import models


# Create your models here.

class Slider(models.Model):
    nom = models.CharField(max_length=200)
    image = models.ImageField(null=True)
    description = models.TextField(null=True, blank=True)
