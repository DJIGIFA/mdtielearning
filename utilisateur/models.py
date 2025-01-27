from django.db import models

# Create your models here.


from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.text import slugify


# Create your models here.


# Les type de compte utilisateur
class Utilisateur(AbstractUser):
    TYPE_COMPTE = [
        ("Admin", "Admin"),
        ("Apprenant", "Apprenant"),
        ("Instructeur", "Instructeur"),
    ]
    #
    GENRE = [
        ("Homme", "Homme"),
        ("Femme", "Femme"),
    ]

    avatar = models.ImageField(null=True, blank=True)

    type_compte = models.CharField(max_length=300, choices=TYPE_COMPTE)
    numero = models.CharField(max_length=200, blank=True, null=True)
    sexe = models.CharField(max_length=30, verbose_name="Genre", blank=True, null=True)
    quartier = models.CharField(max_length=300, verbose_name="Quartier / ville", blank=True, null=True,default="N/A")
    travail = models.CharField(max_length=300, blank=True, null=True)
    date_naissance = models.DateField(auto_now_add=True, blank=True, null=True)
    mail_verifier = models.BooleanField(default=False)
    status = models.BooleanField(default=True)

    cv = models.FileField(null=True, blank=True)
    attestation = models.FileField(null=True, blank=True)

    def __str__(self):
        return f"{self.first_name} ({self.username})"

    @property
    def nombre_cour(self):
        return len(self.cour_set.all())



    @property
    def somme_payer(self):
        return sum(i.montant for i in self.cour_set.all())

    @property
    def nombre_formation(self):
        return len(self.formation_set.all())


    @property
    def nombre_apprenant(self):
        return sum(len(f.cour_set.all()) for f in self.formation_set.all())




class Universite(models.Model):
    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE)

    nom = models.CharField(max_length=500, null=False, blank=False)
    date_debut = models.DateField(auto_now_add=True, blank=True, null=True)
    status = models.BooleanField(default=True)
    slug = models.SlugField(editable=False, blank=True)

    def __str__(self):
        return self.nom

    def _get_unique_slug(self):
        slug = slugify(self.nom)
        unique_slug = slug
        num = 1
        while Universite.objects.filter(slug=unique_slug).exists():
            unique_slug = "{}-{}".format(slug, num)
            num += 1
        return unique_slug

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self._get_unique_slug()
        super().save()



class PasswordReset(models.Model):
    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE)
    time = models.FloatField()
    utiliser = models.BooleanField(default=False)


class Verification_email(models.Model):
    email = models.EmailField()
    code = models.CharField(max_length=512)

    valide = models.BooleanField(default=True)
    date = models.DateField(auto_now=True)
