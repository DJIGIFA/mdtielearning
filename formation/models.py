from django.db import models
from django.utils.text import slugify

from utilisateur.models import Utilisateur

from root.outil import MOYEN_PAIEMENT


# Create your models here.
def minute_to_heure(minute: int):
    h = int(minute / 60)
    minute = int(minute % 60)

    if h > 0:
        return f"{h} h : {minute} mn"
    return f"{minute} mn"


class Categorie(models.Model):
    nom = models.CharField(max_length=200)
    image = models.ImageField()
    slug = models.SlugField()

    @property
    def sous_categorie(self):
        return self.souscategorie_set.all()

    def _get_unique_slug(self):
        slug = slugify(self.nom)
        unique_slug = slug
        num = 1
        while Categorie.objects.filter(slug=unique_slug).exists():
            unique_slug = "{}-{}".format(slug, num)
            num += 1
        return unique_slug

    @property
    def nombre_formation(self):
        return sum(len(d.all_formation ) for d in self.souscategorie_set.all() )

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self._get_unique_slug()
        super().save()


class SousCategorie(models.Model):
    nom = models.CharField(max_length=200)
    image = models.ImageField()
    slug = models.SlugField()
    categorie = models.ForeignKey(Categorie, on_delete=models.CASCADE)

    @property
    def all_formation(self):
        return self.formation_set.all()

    @property
    def nombre_formation(self):
        return len(self.all_formation)

    def _get_unique_slug(self):
        slug = slugify(self.nom)
        unique_slug = slug
        num = 1
        while SousCategorie.objects.filter(slug=unique_slug).exists():
            unique_slug = "{}-{}".format(slug, num)
            num += 1
        return unique_slug

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self._get_unique_slug()
        super().save()

    # def save(self, *args, **kwargs):
    #     self.slug = slugify(self.title)
    #     super(GeeksModel, self).save(*args, **kwargs)


class Formation(models.Model):
    nom = models.CharField(max_length=200)
    miniature = models.ImageField()
    prix = models.FloatField()

    slug = models.SlugField()

    sous_categorie = models.ForeignKey(SousCategorie, on_delete=models.CASCADE)
    instructeur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE)

    nombre_heur = models.FloatField()

    description = models.TextField(null=True, blank=True)
    prerequis = models.TextField(null=True, blank=True)
    profile_destine = models.TextField(null=True, blank=True)
    objectif_du_cours = models.TextField(null=True, blank=True)

    publier = models.BooleanField(default=False)
    moderer = models.BooleanField(default=False)
    ajout_terminer = models.BooleanField(default=False)

    date = models.DateField(auto_now_add=True)
    date_de_publication = models.DateField(auto_now_add=True)
    dernier_mise_a_jour = models.DateField(auto_now=True)

    @property
    def nombre_apprenant(self):
        return len(self.cour_set.all())

    @property
    def montant_achter(self):
        return sum([cour.montant for cour in self.cour_set.all()])

    @property
    def all_chaptire(self):
        return self.chapitre_set.all()

    @property
    def nombre_chaptire(self):
        return len(self.chapitre_set.all())

    @property
    def nombre_heur_str(self):
        return minute_to_heure(self.nombre_heur)

    @property
    def status(self):

        status = ""
        status += "En ligne" if self.publier else " Hors ligne"
        status += ", moderer" if self.moderer else ""
        status += ", Non terminer" if not self.ajout_terminer else ", terminer"

        return status

    @property
    def qcm(self):
        return self.qcm_set.all()

    def _get_unique_slug(self):
        slug = slugify(self.nom)
        unique_slug = slug
        num = 1
        while Formation.objects.filter(slug=unique_slug).exists():
            unique_slug = "{}-{}".format(slug, num)
            num += 1
        return unique_slug

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self._get_unique_slug()
        super().save()



class Chapitre(models.Model):
    nom = models.CharField(max_length=200)
    formation = models.ForeignKey(Formation, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    ordre = models.IntegerField(default=0)


    @property
    def nombre_video(self):
        return len(self.video_set.all())

    @property
    def all_video(self):
        return self.video_set.all()

    @property
    def duree(self):
        return f"{minute_to_heure(sum([video.duree for video in self.video_set.all()]))}"


class Video(models.Model):
    nom = models.CharField(max_length=200)
    duree = models.IntegerField()
    video = models.FileField()

    ordre = models.IntegerField()

    chapitre = models.ForeignKey(Chapitre, on_delete=models.CASCADE)

    @property
    def duree_str(self):
        return f"{minute_to_heure(self.duree)}"


class Cour(models.Model):
    apprenant = models.ForeignKey(Utilisateur, on_delete=models.CASCADE)
    formation = models.ForeignKey(Formation, on_delete=models.CASCADE)

    montant = models.FloatField()
    date = models.DateField(auto_now_add=True)

    progression = models.FloatField(default=0)

    terminer = models.BooleanField(default=False)


class Suive(models.Model):
    apprenant = models.ForeignKey(Utilisateur, on_delete=models.CASCADE)
    souscategorie = models.ForeignKey(SousCategorie, on_delete=models.CASCADE)

    date = models.DateField(auto_now_add=True)

    terminer = models.BooleanField(default=False)


class VideoVue(models.Model):
    video = models.ForeignKey(Video, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)

    cour = models.ForeignKey(Cour, on_delete=models.CASCADE)


class Temoignage(models.Model):
    apprenant = models.ForeignKey(Utilisateur, on_delete=models.CASCADE)
    formation = models.ForeignKey(Formation, on_delete=models.CASCADE)

    message = models.TextField()

    vue = models.BooleanField(default=False)
    moderer = models.BooleanField(default=False)
    actif = models.BooleanField(default=True)

    date = models.DateField(auto_now_add=True)


class Discution(models.Model):
    apprenant = models.ForeignKey(Utilisateur, on_delete=models.CASCADE)
    formation = models.ForeignKey(Formation, on_delete=models.CASCADE)
    message = models.TextField()
    envoyer_par_apprenant = models.BooleanField()

    date = models.DateField(auto_now_add=True)
    lue = models.BooleanField(default=False)


class SeanceTravail(models.Model):
    nom = models.CharField(max_length=512)

    apprenant = models.ForeignKey(Utilisateur, on_delete=models.CASCADE)
    formation = models.ForeignKey(Formation, on_delete=models.CASCADE)

    lien_de_la_reunion = models.URLField()

    confirmer_par_apprenant = models.BooleanField(default=False)
    confirmer_par_instructeur = models.BooleanField(default=False)

    date = models.DateTimeField(auto_now_add=True)
    date_de_la_reunion = models.DateField()

    # def _get_unique_slug(self):
    #     slug = slugify(self.nom)
    #     unique_slug = slug
    #     num = 1
    #     while SeanceTravail.objects.filter(slug=unique_slug).exists():
    #         unique_slug = "{}-{}".format(slug, num)
    #         num += 1
    #     return unique_slug

    # def save(self, *args, **kwargs):
    #     if not self.slug:
    #         self.slug = self._get_unique_slug()
    #     super().save()


class Qcm(models.Model):
    nom = models.CharField(max_length=2500)
    description = models.TextField()
    duree = models.IntegerField()

    formation = models.ForeignKey(Formation, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)

    @property
    def point_total(self):
        return sum([q.point for q in self.question_set.all()])

    @property
    def questions(self):
        return self.question_set.all()




class Question(models.Model):
    question = models.TextField()
    qcm = models.ForeignKey(Qcm, on_delete=models.CASCADE)
    point = models.IntegerField()

    @property
    def all_response(self):
        return self.reponse_set.all()


class Reponse(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    reponse = models.TextField()
    correcte = models.BooleanField()
    date = models.DateField(auto_now_add=True)

    @property
    def etat(self):
        return "Correcte" if self.correcte else "Incorrecte"


class Examen(models.Model):
    nom = models.CharField(max_length=250)
    reponse = models.CharField(max_length=250)
    apprenant = models.ForeignKey(Utilisateur, on_delete=models.CASCADE)
    qcm = models.ForeignKey(Qcm, on_delete=models.CASCADE)

    duree = models.IntegerField()
    point = models.IntegerField()
    correct = models.BooleanField(default=False)

    date = models.DateField(auto_now_add=True)


class Participer(models.Model):
    apprenant = models.ForeignKey(Utilisateur, on_delete=models.CASCADE)
    qcm = models.ForeignKey(Qcm, on_delete=models.CASCADE)

    point = models.IntegerField(null=True, blank=True)

    date = models.DateField(auto_now_add=True)


class ResultatExamen(models.Model):
    examen = models.ForeignKey(Examen, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    response = models.ForeignKey(Reponse, on_delete=models.CASCADE)


# gestion du paiement


class PaiementFormation(models.Model):
    order_id = models.CharField(max_length=512, unique=True)
    payer = models.BooleanField(default=False)

    moyen_paiement = models.CharField(max_length=50, choices=MOYEN_PAIEMENT)

    date_soumission = models.DateTimeField(auto_now_add=True)
    date_validation = models.DateTimeField(null=True)

    montant = models.FloatField()
    formation = models.ForeignKey(Formation, on_delete=models.CASCADE)
    client = models.ForeignKey(Utilisateur, on_delete=models.CASCADE)

    numero = models.CharField(max_length=30, null=True)

    strip_link = models.URLField(null=True)