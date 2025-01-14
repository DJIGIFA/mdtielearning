import datetime
import json
import string

import requests
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.decorators.csrf import csrf_exempt

from formation.models import Categorie, SousCategorie, Formation, Cour, Chapitre, Discution, Temoignage, Video, \
    VideoVue, SeanceTravail, Qcm, Question, Reponse, Examen, ResultatExamen, PaiementFormation, Suive, Participer
from root.code_paiement import paiement_login, paiement_password, message_trouver_mais_pas_confirmer, \
    message_trouver_et_comfirmer, formation_order_id_len
from root.outil import base64_to_image, get_order_id, verifier_numero, paiement_orange, paiement_moov, sama_pay, \
    stripe_pay, verifier_status
from utilisateur.models import Utilisateur

# Create your views here.

"""
Formations
"""


@csrf_exempt
def add_formation(request):
    response_data = {'message': "requette invalide", 'etat': False}

    if request.method == "POST":
        form = dict()
        try:
            form = json.loads(request.body.decode("utf-8"))
        except:
            ...

        if (
                "nom" in form
                and "miniature" in form
                and "prix" in form
                and "sous_categorie_slug" in form
                and "instructeur_id" in form
                and "nombre_heur" in form
        ):
            nom = form.get("nom")
            miniature_64 = form.get("miniature")
            prix = form.get("prix")
            sous_categorie_slug = form.get("sous_categorie_slug")
            instructeur_id = form.get("instructeur_id")
            nombre_heur = form.get("nombre_heur")

            miniature = base64_to_image(miniature_64)

            # trouver le sous categorie

            sous_categorie = SousCategorie.objects.all().filter(slug=sous_categorie_slug).first()

            if not sous_categorie:
                response_data["message"] = "sous categorie non trouve"
                response_data["etat"] = False
            else:

                # trouver instructeur

                instructeur = Utilisateur.objects.all().filter(id=instructeur_id).first()

                if not instructeur:
                    response_data["message"] = "instructeur non trouve"
                    response_data["etat"] = False
                else:

                    if instructeur.type_compte != "instructeur":
                        response_data["message"] = "seul les instructeurs peuvent publier des formations"
                        response_data["etat"] = False
                    else:
                        new_formation = Formation(
                            nom=nom,
                            miniature=miniature,
                            prix=prix,
                            sous_categorie=sous_categorie,
                            nombre_heur=nombre_heur,
                            instructeur=instructeur,
                        )

                        new_formation.save()

                        # TODO send mail ??

                        response_data["message"] = "success"
                        response_data["etat"] = True

    return HttpResponse(json.dumps(response_data), content_type="application/json")


@csrf_exempt
def get_formation(request):
    response_data = {'message': "requette invalide", 'etat': False}

    if request.method == "POST":
        form = dict()
        try:
            form = json.loads(request.body.decode("utf-8"))
        except:
            ...

        all_formation = []
        filter = False

        if True:

            # publier = form.get("publier")
            # moderer = form.get("moderer")
            # ajout_terminer = form.get("ajout_terminer")

            if "sous_categorie_slug" in form:
                sous_categorie_slug = form.get("sous_categorie_slug")
                sous_categorie = SousCategorie.objects.all().filter(slug=sous_categorie_slug).first()

                if sous_categorie:
                    all_formation = Formation.objects.all().filter(sous_categorie=sous_categorie)
                    filter = True
                else:
                    response_data["message"] = "sous categorie non trouver"

            elif "id" in form:
                formation_id = form.get("id")
                all_formation = Formation.objects.all().filter(id=formation_id)
                filter = True
                # if formation:
                #     all_formation = formation
                #     filter = True
                # else:
                #     response_data["message"] = "formation non trouver"

            elif "instructeur_id" in form:
                instructeur_id = form.get("instructeur_id")
                instructeur = Utilisateur.objects.all().filter(id=instructeur_id).first()

                if instructeur:
                    all_formation = Formation.objects.all().filter(instructeur=instructeur)
                    filter = True
                else:
                    response_data["message"] = "instructeur non trouver"

            elif "sous_categorie_slug" in form:
                apprenant_id = form.get("apprenant_id")
                apprenant = Utilisateur.objects.all().filter(id=apprenant_id).first()

                if apprenant:

                    all_cour = Cour.objects.all().filter(apprenant=apprenant)

                    for cour in all_cour:
                        all_formation.append(cour.formation)
                    filter = True
                else:
                    response_data["message"] = "apprenant non trouver"

            elif "all" in form:
                all_formation = Formation.objects.all()
                filter = True

            if filter:
                if len(all_formation) > 0:
                    formations = list()

                    for f in all_formation:

                        if ("publier" in form and f.publier != form.get("publier")) or (
                                "moderer" in form and f.moderer != form.get("moderer")) or (
                                "ajout_terminer" in form and f.ajout_terminer != form.get("ajout_terminer")):
                            continue

                        formations.append(
                            {
                                "nom": f.nom,
                                "id": f.id,
                                "miniature": f.miniature.url if f.miniature else None,
                                "prix": f.prix,
                                "slug": f.slug,
                                "sous_categorie_slug": f.sous_categorie.slug,
                                "instructeur_id": f.instructeur.id,
                                "nombre_heur": f.nombre_heur_str,
                                "description": f.description,
                                "prerequis": f.prerequis,
                                "profile_destine": f.profile_destine,
                                "objectif_du_cours": f.objectif_du_cours,
                                "publier": f.publier,
                                "moderer": f.moderer,
                                "ajout_terminer": f.ajout_terminer,

                                "date": str(f.date),
                                "date_de_publication": str(f.date_de_publication) if f.date_de_publication else None,
                                "dernier_mise_a_jour": str(f.dernier_mise_a_jour),

                                "nombre_apprenant": f.nombre_apprenant,
                                "montant_achter": f.montant_achter,
                            }
                        )

                    if len(formations) > 0:
                        response_data['etat'] = True
                        response_data["message"] = "success"
                        response_data["donnee"] = formations
                    else:
                        response_data["message"] = "vide"

                else:
                    response_data["message"] = "vide"
        else:
            ...

    return HttpResponse(json.dumps(response_data), content_type="application/json")


@csrf_exempt
def get_all_formation(request):
    response_data = {'message': "requette invalide", 'etat': False}

    if request.method == "POST":
        form = dict()
        try:
            form = json.loads(request.body.decode("utf-8"))
        except:
            ...

        all_formation = Formation.objects.all()
        formations = list()
        for f in all_formation:
            formations.append(
                {
                    "nom": f.nom,
                    "id": f.id,
                    "miniature": f.miniature.url if f.miniature else None,
                    "prix": f.prix,
                    "slug": f.slug,
                    "sous_categorie_slug": f.sous_categorie.slug,
                    "instructeur_id": f.instructeur.id,
                    "instructeur_first_name": f.instructeur.first_name,
                    "instructeur_last_name": f.instructeur.last_name,
                    "instructeur_avatar": f.instructeur.avatar.url if f.instructeur.avatar else None,
                    "nombre_heur": f.nombre_heur_str,
                    "description": f.description,
                    "prerequis": f.prerequis,
                    "profile_destine": f.profile_destine,
                    "objectif_du_cours": f.objectif_du_cours,
                    "publier": f.publier,
                    "moderer": f.moderer,
                    "ajout_terminer": f.ajout_terminer,

                    "date": str(f.date),
                    "date_de_publication": str(f.date_de_publication) if f.date_de_publication else None,
                    "dernier_mise_a_jour": str(f.dernier_mise_a_jour),

                    "nombre_apprenant": f.nombre_apprenant,
                    "montant_achter": f.montant_achter,
                }
            )

        if len(formations) > 0:
            response_data['etat'] = True
            response_data["message"] = "success"
            response_data["donnee"] = formations
        else:
            response_data["message"] = "vide"

    return HttpResponse(json.dumps(response_data), content_type="application/json")


@csrf_exempt
def set_formation(request):
    response_data = {'message': "requette invalide", 'etat': False}

    if request.method == "POST":
        form = dict()
        try:
            form = json.loads(request.body.decode("utf-8"))
        except:
            ...

        if "slug" in form:
            slug = form.get("slug")
            formation = Formation.objects.all().filter(slug=slug).first()

            if formation:
                modifier = False
                if "nom" in form:
                    nom = form.get("nom")
                    formation.nom = nom
                    modifier = True
                if "miniature" in form:
                    miniature_64 = form.get("miniature")
                    miniature = base64_to_image(miniature_64)
                    formation.miniature = miniature
                    modifier = True

                if "prix" in form:
                    prix = form.get("prix")

                    formation.prix = prix
                    modifier = True

                if "sous_categorie_slug" in form:
                    sous_categorie_slug = form.get("sous_categorie_slug")

                    sous_categorie = SousCategorie.objects.all().filter(slug=sous_categorie_slug).first()
                    if sous_categorie:
                        formation.sous_categorie = sous_categorie
                        modifier = True
                    else:
                        response_data["message"] = "sous categorie non trouver"

                if "instructeur_id" in form:
                    instructeur_id = form.get("instructeur_id")

                    instructeur = Utilisateur.objects.all().filter(id=instructeur_id).first()
                    if instructeur:
                        formation.instructeur = instructeur
                        modifier = True
                    else:
                        response_data["message"] = "instructeur non trouver"

                if "nombre_heur" in form:
                    nombre_heur = form.get("nombre_heur")

                    formation.nombre_heur = nombre_heur
                    modifier = True

                if "description" in form:
                    description = form.get("description")

                    formation.description = description
                    modifier = True

                if "prerequis" in form:
                    prerequis = form.get("prerequis")

                    formation.prerequis = prerequis
                    modifier = True

                if "profile_destine" in form:
                    profile_destine = form.get("profile_destine")


                    formation.profile_destine = profile_destine
                    modifier = True

                if "objectif_du_cours" in form:
                    objectif_du_cours = form.get("objectif_du_cours")

                    formation.objectif_du_cours = objectif_du_cours
                    modifier = True

                if "publier" in form:
                    publier = form.get("publier")

                    formation.publier = publier
                    modifier = True

                if "moderer" in form:
                    moderer = form.get("moderer")

                    formation.moderer = moderer
                    modifier = True

                if "ajout_terminer" in form:
                    ajout_terminer = form.get("ajout_terminer")

                    formation.ajout_terminer = ajout_terminer
                    modifier = True

                # if "ajout_terminer" in form:
                #     ajout_terminer = form.get("ajout_terminer")
                #
                #     formation.ajout_terminer = ajout_terminer
                #     modifier = True

                # enregistrer
                if modifier:
                    formation.save()
                    response_data["etat"] = True
                    response_data["message"] = "success"



            else:
                response_data["message"] = "formation non trouver"
                response_data["etat"] = False

    return HttpResponse(json.dumps(response_data), content_type="application/json")


@csrf_exempt
def del_formation(request):
    response_data = {'message': "requette invalide", 'etat': False}

    if request.method == "POST":
        form = dict()
        try:
            form = json.loads(request.body.decode("utf-8"))
        except:
            ...

        if "slug" in form or "id" in form:
            formation = None
            if "slug" in form:
                slug = form.get("slug")
                formation = Formation.objects.all().filter(slug=slug).first()
            else:
                id = form.get("id")
                formation = Formation.objects.all().filter(id=id).first()

            if formation:

                cours = Cour.objects.all().filter(formation=formation)
                if len(cours) == 0:
                    formation.delete()

                    response_data["etat"] = True
                    response_data["message"] = "success"
                else:
                    response_data["message"] = "impossible de supprimer cette formation, vous pouvez le desactiver"
            else:
                response_data["etat"] = False
                response_data["message"] = "formation non trouver"

    return HttpResponse(json.dumps(response_data), content_type="application/json")


@csrf_exempt
def get_formation_detaille(request, slug):
    response_data = {'message': "requette invalide", 'etat': False}

    formation = Formation.objects.all().filter(slug=slug).first()

    if formation:
        form_json = {
            "nom": formation.nom,
            "id": formation.id,
            "miniature": formation.miniature.url if formation.miniature else None,
            "prix": formation.prix,
            "slug": formation.slug,
            "sous_categorie_slug": formation.sous_categorie.slug,
            "instructeur_id": formation.instructeur.id,
            "nombre_heur": formation.nombre_heur_str,
            "description": formation.description,
            "prerequis": formation.prerequis,
            "profile_destine": formation.profile_destine,
            "objecti_du_cours": formation.objectif_du_cours,
            "publier": formation.publier,
            "moderer": formation.moderer,
            "ajout_terminer": formation.ajout_terminer,

            "date": str(formation.date),
            "date_de_publication": str(
                formation.date_de_publication) if formation.date_de_publication else None,
            "dernier_mise_a_jour": str(formation.dernier_mise_a_jour),

            "nombre_apprenant": formation.nombre_apprenant,
            "montant_achter": formation.montant_achter,
        }

        response_data["etat"] = True
        response_data["message"] = "success"
        response_data["donnee"] = form_json
    else:
        response_data["message"] = "formation non trouver"

    return HttpResponse(json.dumps(response_data), content_type="application/json")


@csrf_exempt
def get_formation_un(request):
    response_data = {'message': "requette invalide", 'etat': False}

    if request.method == "POST":
        form = dict()
        try:
            form = json.loads(request.body.decode("utf-8"))
        except:
            ...

        filtrer = False
        if "id" in form:
            formation_id = form.get("id")

            formation = Formation.objects.all().filter(id=formation_id).first()
            filtrer = True

        if "slug" in form:
            formation_slug = form.get("slug")

            formation = Formation.objects.all().filter(slug=formation_slug).first()
            filtrer = True

        if filtrer:
            form_json = {
                "nom": formation.nom,
                "miniature": formation.miniature.url if formation.miniature else None,
                "prix": formation.prix,
                "slug": formation.slug,
                "sous_categorie_slug": formation.sous_categorie.slug,
                "instructeur_id": formation.instructeur.id,
                "nombre_heur": formation.nombre_heur_str,
                "description": formation.description,
                "prerequis": formation.prerequis,
                "profile_destine": formation.profile_destine,
                "objecti_du_cours": formation.objectif_du_cours,
                "publier": formation.publier,
                "moderer": formation.moderer,
                "ajout_terminer": formation.ajout_terminer,

                "date": str(formation.date),
                "date_de_publication": str(
                    formation.date_de_publication) if formation.date_de_publication else None,
                "dernier_mise_a_jour": str(formation.dernier_mise_a_jour),

                "nombre_apprenant": formation.nombre_apprenant,
                "montant_achter": formation.montant_achter,
            }

            response_data["etat"] = True
            response_data["message"] = "success"
            response_data["donnee"] = form_json

    return HttpResponse(json.dumps(response_data), content_type="application/json")


"""
Categorie 
"""


@csrf_exempt
def add_categorie(request):
    response_data = {'message': "requette invalide", 'etat': False}

    if request.method == "POST":
        form = dict()
        try:
            form = json.loads(request.body.decode("utf-8"))
        except:
            ...

        if "nom" in form and "image" in form:
            nom = form.get("nom")
            image_data = form.get("image")
            image = base64_to_image(image_data)

            new_categorie = Categorie(nom=nom, image=image)
            new_categorie.save()

            response_data["etat"] = True
            response_data["id"] = new_categorie.id
            response_data["slug"] = new_categorie.slug
            response_data["message"] = "success"

        else:
            ...
        # requette invalide

    return HttpResponse(json.dumps(response_data), content_type="application/json")


@csrf_exempt
def del_categorie(request):
    response_data = {'message': "requette invalide", 'etat': False}

    if request.method == "POST":
        form = dict()
        try:
            form = json.loads(request.body.decode("utf-8"))
        except:
            ...

        if "id" in form or "slug" in form:
            id = form.get("id")
            slug = form.get("slug")
            if id:
                categorie_from_database = Categorie.objects.all().filter(id=id).first()
            else:
                categorie_from_database = Categorie.objects.all().filter(slug=slug).first()

            if not categorie_from_database:
                response_data["message"] = "categorie non trouvé"
            else:
                if len(categorie_from_database.sous_categorie) > 0:
                    response_data[
                        "message"] = f"cette categorie possède {len(categorie_from_database.sous_categorie)} sous categorie"
                else:
                    categorie_from_database.delete()
                    response_data["etat"] = True
                    response_data["message"] = "success"

    return HttpResponse(json.dumps(response_data), content_type="application/json")


@csrf_exempt
def get_categorie(request):
    response_data = {'message': "requette invalide", 'etat': False}

    if request.method == "POST":
        form = dict()
        try:
            form = json.loads(request.body.decode("utf-8"))
        except:
            ...

        all_categorie = Categorie.objects.all()
        filtrer = False

        categorie_id = form.get("id")
        if categorie_id:
            all_categorie = all_categorie.filter(id=categorie_id)
            filtrer = True

        categorie_slug = form.get("slug")
        if categorie_slug:
            all_categorie = all_categorie.filter(slug=categorie_slug)
            filtrer = True

        categorie_all = form.get("all")
        if categorie_all:
            all_categorie = Categorie.objects.all()
            filtrer = True

        if filtrer:

            categories = list()
            for c in all_categorie:
                categories.append(
                    {
                        "id": c.id,
                        "nom": c.nom,
                        "slug": c.slug,
                        "image": c.image.url if c.image else None,
                    }
                )
            if categories:
                response_data["etat"] = True
                response_data["donnee"] = categories
                response_data["message"] = "success"
            else:
                response_data["message"] = "Aucun categorie trouver"

    return HttpResponse(json.dumps(response_data), content_type="application/json")


@csrf_exempt
def get_categorie_un(request, id):
    response_data = {'message': "requette invalide", 'etat': False}
    categorie = Categorie.objects.all().filter(id=id).first()

    if categorie:
        categorie_data = {
            "id": categorie.id,
            "nom": categorie.nom,
            "slug": categorie.slug,
            "image": categorie.image.url if categorie.image else None,
        }

        response_data["etat"] = True
        response_data["donnee"] = categorie_data
        response_data["message"] = "success"
    else:
        response_data["message"] = "categorie non trouver"

    return HttpResponse(json.dumps(response_data), content_type="application/json")


@csrf_exempt
def set_categorie(request):
    response_data = {'message': "requette invalide", 'etat': False}

    if request.method == "POST":
        form = dict()
        try:
            form = json.loads(request.body.decode("utf-8"))
        except:
            ...

        if "id" in form or "slug" in form:

            if "id" in form:
                id = form.get("id")
                categorie_from_database = Categorie.objects.all().filter(id=id).first()
            else:
                slug = form.get("slug")
                categorie_from_database = Categorie.objects.all().filter(slug=slug).first()

            if not categorie_from_database:
                response_data["message"] = "categorie non trouvé"
            else:
                modifier = False
                if "nom" in form:
                    nom = form.get("nom")

                    categorie_from_database.nom = nom
                    modifier = True

                if "image" in form:
                    image_data = form.get("image")

                    image = base64_to_image(image_data)
                    categorie_from_database.image = image
                    modifier = True

                if modifier:
                    categorie_from_database.save()
                    response_data["etat"] = True
                    response_data["message"] = "success"

    return HttpResponse(json.dumps(response_data), content_type="application/json")


"""
SousCategorie 
"""


@csrf_exempt
def add_sous_categorie(request):
    response_data = {'message': "requette invalide", 'etat': False}

    if request.method == "POST":
        form = dict()
        try:
            form = json.loads(request.body.decode("utf-8"))
        except:
            ...

        if "nom" in form and "image" in form and "categorie_slug":
            nom = form.get("nom")
            image_data = form.get("image")
            categorie_slug = form.get("categorie_slug")

            categorie_from_database = Categorie.objects.all().filter(slug=categorie_slug).first()
            if not categorie_from_database:
                response_data["message"] = "categorie non trouvé"
            else:
                image = base64_to_image(image_data)

                new_sous_categorie = SousCategorie(nom=nom, image=image, categorie=categorie_from_database)
                new_sous_categorie.save()

                response_data["etat"] = True
                response_data["id"] = new_sous_categorie.id
                response_data["slug"] = new_sous_categorie.slug
                response_data["message"] = "success"

        else:
            ...
        # requette invalide

    return HttpResponse(json.dumps(response_data), content_type="application/json")


@csrf_exempt
def del_sous_categorie(request):
    response_data = {'message': "requette invalide", 'etat': False}

    if request.method == "POST":
        form = dict()
        try:
            form = json.loads(request.body.decode("utf-8"))
        except:
            ...

        if "id" in form or "slug" in form:
            id = form.get("id")
            slug = form.get("slug")
            if id:
                sous_categorie_from_database = SousCategorie.objects.all().filter(id=id).first()
            else:
                sous_categorie_from_database = SousCategorie.objects.all().filter(slug=slug).first()

            if not sous_categorie_from_database:
                response_data["message"] = "categorie non trouvé"
            else:
                if len(sous_categorie_from_database.all_formation) > 0:
                    response_data[
                        "message"] = f"cette categorie possède {len(sous_categorie_from_database.all_formation)} formation"
                else:
                    sous_categorie_from_database.delete()
                    response_data["etat"] = True
                    response_data["message"] = "success"

    return HttpResponse(json.dumps(response_data), content_type="application/json")


@csrf_exempt
def get_sous_categorie(request):
    response_data = {'message': "requette invalide", 'etat': False}

    if request.method == "POST":
        form = dict()
        try:
            form = json.loads(request.body.decode("utf-8"))
        except:
            ...

        filter = False
        all_sous_categorie = SousCategorie.objects.all()

        if "categorie_slug" in form:
            categorie_slug = form.get("categorie_slug")

            categorie_from_database = Categorie.objects.all().filter(slug=categorie_slug).first()

            if categorie_from_database:
                all_sous_categorie = all_sous_categorie.filter(categorie=categorie_from_database)
                filter = True
            else:
                response_data["message"] = "categorie non trouver"

        elif "id" in form:
            id = form.get("id")
            all_sous_categorie = all_sous_categorie.filter(id=id)
            filter = True

        elif "slug" in form:
            slug = form.get("slug")
            all_sous_categorie = all_sous_categorie.filter(slug=slug)
            filter = True

        else:
            filter = True
            all_sous_categorie = SousCategorie.objects.all()

        if filter:

            sous_categorie = list()
            for sc in all_sous_categorie:
                sous_categorie.append(
                    {
                        "id": sc.id,
                        "nom": sc.nom,
                        "slug": sc.slug,
                        "categorie_slug": sc.categorie.slug,
                        "image": sc.image.url,
                        "formation": [
                            {
                                "id": formation.id,
                                "nom": formation.nom,
                                "slug": formation.slug,
                                "miniature": formation.miniature.url if formation.miniature else None,
                                "publier": formation.publier,
                                "date": str(formation.date),
                                "nombre_heur": formation.nombre_heur_str,
                            } for formation in sc.all_formation
                        ]
                    }
                )

            if len(sous_categorie) > 0:

                response_data["etat"] = True
                response_data["donnee"] = sous_categorie
                response_data["message"] = "success"
            else:
                response_data["message"] = "vide"

    return HttpResponse(json.dumps(response_data), content_type="application/json")


@csrf_exempt
def get_sous_categorie_un(request, id):
    response_data = {'message': "requette invalide", 'etat': False}

    sous_categorie = SousCategorie.objects.all().filter(id=id).first()

    if sous_categorie:
        sous_categorie_data = {
            "id": sous_categorie.id,
            "nom": sous_categorie.nom,
            "slug": sous_categorie.slug,
            "categorie_slug": sous_categorie.categorie.slug,
            "image": sous_categorie.image.url if sous_categorie.image else None,
            "formation": [
                {
                    "id": formation.id,
                    "nom": formation.nom,
                    "miniature": formation.miniature.url if formation.miniature else None,
                    "publier": formation.publier,
                    "date": str(formation.date),
                    "nombre_heur": formation.nombre_heur_str,
                } for formation in sous_categorie.all_formation
            ]
        }

        response_data["etat"] = True
        response_data["message"] = "success"
        response_data["donnee"] = sous_categorie_data
    else:
        response_data["message"] = "sous categorie non trouver"

    return HttpResponse(json.dumps(response_data), content_type="application/json")


@csrf_exempt
def set_sous_categorie(request):
    response_data = {'message': "requette invalide", 'etat': False}

    if request.method == "POST":
        form = dict()
        try:
            form = json.loads(request.body.decode("utf-8"))
        except:
            ...

        if "id" in form or "slug" in form:
            id = form.get("id")
            slug = form.get("slug")
            if id:
                sous_categorie_from_database = SousCategorie.objects.all().filter(id=id).first()
            else:
                sous_categorie_from_database = SousCategorie.objects.all().filter(slug=slug).first()

            if not sous_categorie_from_database:
                response_data["message"] = "Sous categorie non trouve"
            else:
                modifier = False
                if "nom" in form:
                    nom = form.get("nom")

                    sous_categorie_from_database.nom = nom
                    modifier = True

                if "image" in form:
                    image_data = form.get("image")

                    image = base64_to_image(image_data)
                    sous_categorie_from_database.image = image
                    modifier = True

                if "categorie_slug" in form:
                    categorie_slug = form.get("categorie_slug")

                    categorie_from_database = Categorie.objects.all().filter(slug=categorie_slug).first()

                    if categorie_from_database:
                        sous_categorie_from_database.categorie = categorie_from_database
                        modifier = True
                    else:
                        response_data["etat"] = True
                        response_data["message"] = "categorie non trouve"

                if modifier:
                    sous_categorie_from_database.save()
                    response_data["etat"] = True
                    response_data["message"] = "success"

    return HttpResponse(json.dumps(response_data), content_type="application/json")


# Chapitre
@csrf_exempt
def add_chapitre(request):
    response_data = {'message': "requette invalide", 'etat': False}

    if request.method == "POST":
        form = dict()
        try:
            form = json.loads(request.body.decode("utf-8"))
        except:
            ...

        if "nom" in form and "formation_slug" in form:
            nom = form.get("nom")
            formation_slug = form.get("formation_slug")

            formation = Formation.objects.all().filter(slug=formation_slug).first()

            if formation:
                new_chapitre = Chapitre(nom=nom, formation=formation)
                new_chapitre.save()
                response_data["etat"] = True
                response_data["message"] = "success"
            else:
                response_data["message"] = "formation non trouver"

    return HttpResponse(json.dumps(response_data), content_type="application/json")


@csrf_exempt
def get_chapitre(request):
    response_data = {'message': "requette invalide", 'etat': False}

    if request.method == "POST":
        form = dict()
        try:
            form = json.loads(request.body.decode("utf-8"))
        except:
            ...

        if "formation_slug" in form:
            formation_slug = form.get("formation_slug")

            formation = Formation.objects.all().filter(slug=formation_slug).first()

            if formation:
                all_chaptire = formation.all_chaptire

                filtrer = False

                categorie_id = form.get("id")
                if categorie_id:
                    all_chaptire = all_chaptire.filter(id=categorie_id)
                    filtrer = True

                categorie_slug = form.get("slug")
                if categorie_slug:
                    all_chaptire = all_chaptire.filter(slug=categorie_slug)
                    filtrer = True

                categorie_all = form.get("all")
                if categorie_all:
                    all_chaptire = formation.all_chaptire
                    filtrer = True

                if filtrer:

                    chapitres = list()

                    for ch in all_chaptire:
                        chapitres.append(
                            {
                                "id": ch.id,
                                "nom": ch.nom,
                                "nombre_video": ch.nombre_video,
                                "duree": ch.duree,
                                "video": [
                                    {
                                        "id": video.id,
                                        "nom": video.nom,
                                        "duree": video.duree_str,
                                        "ordre": video.ordre,
                                        "video_url": video.video.url if video.video else None,
                                    } for video in ch.all_video
                                ]
                            }
                        )
                    if chapitres:
                        response_data["etat"] = True
                        response_data["donnee"] = chapitres
                        response_data["message"] = "success"
                    else:
                        response_data["message"] = "vide"

            else:
                response_data["message"] = "formation non trouver"

    return HttpResponse(json.dumps(response_data), content_type="application/json")


@csrf_exempt
def get_chapitre_all(request):
    response_data = {'message': "requette invalide", 'etat': False}

    chapitre = Chapitre.objects.all()

    all_chapitre = list()
    for ch in chapitre:
        all_chapitre.append(
            {
                "id": ch.id,
                "nom": ch.nom,
                "nombre_video": ch.nombre_video.url if ch.nombre_video else None,
                "duree": ch.duree,
            }
        )

    if len(all_chapitre) > 0:
        response_data["etat"] = True
        response_data["message"] = "success"
        response_data["donnee"] = all_chapitre
    else:
        response_data["message"] = "vide"

    return HttpResponse(json.dumps(response_data), content_type="application/json")


@csrf_exempt
def get_chapitre_un(request, id):
    response_data = {'message': "requette invalide", 'etat': False}

    chapitre = Chapitre.objects.all().filter(id=id).first()

    if chapitre:
        chapitre_data = {
            "id": chapitre.id,
            "nom": chapitre.nom,
            "nombre_video": chapitre.nombre_video.url if chapitre.nombre_video else None,
            "duree": chapitre.duree,
        }
        response_data["etat"] = True
        response_data["message"] = "success"
        response_data["donnee"] = chapitre_data
    else:
        response_data["message"] = "chapitre non trouver"

    return HttpResponse(json.dumps(response_data), content_type="application/json")


@csrf_exempt
def set_chapitre(request):
    response_data = {'message': "requette invalide", 'etat': False}

    if request.method == "POST":
        form = dict()
        try:
            form = json.loads(request.body.decode("utf-8"))
        except:
            ...

        if "id" in form and "nom" in form:
            id = form.get("id")
            nom = form.get("nom")

            chapitre = Chapitre.objects.all().filter(id=id).first()

            if chapitre:
                chapitre.nom = nom
                chapitre.save()
                response_data["message"] = "success"
                response_data["etat"] = True
            else:
                response_data["message"] = "chapitre non trouver"

    return HttpResponse(json.dumps(response_data), content_type="application/json")


@csrf_exempt
def del_chapitre(request):
    response_data = {'message': "requette invalide", 'etat': False}

    if request.method == "POST":
        form = dict()
        try:
            form = json.loads(request.body.decode("utf-8"))
        except:
            ...

        if "id" in form:
            id = form.get("id")
            nom = form.get("nom")

            chapitre = Chapitre.objects.all().filter(id=id).first()

            if chapitre:
                if chapitre.nombre_video == 0:
                    chapitre.delete()
                    response_data["message"] = "success"
                    response_data["etat"] = True
                else:
                    response_data['etat'] = False
                    response_data["message"] = f"ce chapitre contient {chapitre.nombre_video} videos"
            else:
                response_data["message"] = "chapitre non trouver"

    return HttpResponse(json.dumps(response_data), content_type="application/json")


@csrf_exempt
def add_discution(request):
    response_data = {'message': "requette invalide", 'etat': False}

    if request.method == "POST":
        form = dict()
        try:
            form = json.loads(request.body.decode("utf-8"))
        except:
            ...

        if "apprenant_id" in form and "formation_slug" in form and "message" in form and "envoyer_par_apprenant" in form:

            apprenant_id = form.get("apprenant_id")
            formation_slug = form.get("formation_slug")
            message = form.get("message")
            envoyer_par_apprenant = form.get("envoyer_par_apprenant")

            # apprenant
            apprenant = Utilisateur.objects.all().filter(id=apprenant_id).first()
            if apprenant:
                # formation
                formation = Formation.objects.all().filter(slug=formation_slug).first()

                if formation:
                    # verifier si l'apprenant a suivie cette formation

                    tmp_cour = Cour.objects.all().filter(apprenant=apprenant, formation=formation)
                    if len(tmp_cour) > 0:
                        new_discution = Discution(apprenant=apprenant, formation=formation, message=message,
                                                  envoyer_par_apprenant=envoyer_par_apprenant)
                        new_discution.save()

                        response_data["etat"] = True
                        response_data["message"] = "success"
                        response_data["id"] = new_discution.id

                    else:
                        response_data["message"] = "Vous ne suivez pas cette formation"
                else:
                    response_data["message"] = "formation non trouver"
            else:
                response_data["message"] = "utilisateur non trouver"

    return HttpResponse(json.dumps(response_data), content_type="application/json")


@csrf_exempt
def get_discution(request):
    response_data = {'message': "requette invalide", 'etat': False}

    if request.method == "POST":
        form = dict()
        try:
            form = json.loads(request.body.decode("utf-8"))
        except:
            ...

        if "apprenant_id" in form and "formation_slug" in form:

            apprenant_id = form.get("apprenant_id")
            formation_slug = form.get("formation_slug")

            all_discution = Discution.objects.all()
            filtrer = False

            apprenant = Utilisateur.objects.all().filter(id=apprenant_id).first()

            if apprenant:
                all_discution = all_discution.filter(apprenant=apprenant)
                filtrer = True

                formation = Formation.objects.all().filter(slug=formation_slug).first()

                if formation:
                    all_discution = all_discution.filter(formation=formation)
                    filtrer = True
                else:
                    response_data["message"] = "formation non trouver"

            else:
                response_data["message"] = "apprenant non trouver"

            if filtrer:
                if len(all_discution) > 0:
                    discutions = list()

                    for disc in all_discution:
                        discutions.append(
                            {
                                "apprenant_id": disc.apprenant.id,
                                "apprenant_first_name": disc.apprenant.first_name,
                                "apprenant_last_name": disc.apprenant.last_name,
                                "formation_slug": disc.formation.slug,
                                "formation_nom": disc.formation.nom,

                                "message": disc.message,
                                "envoyer_par_apprenant": disc.envoyer_par_apprenant,
                                "id": disc.id,
                                "date": str(disc.date),
                                "lue": disc.lue,
                            }
                        )

                    response_data["etat"] = True
                    response_data["donnee"] = discutions
                    response_data["message"] = "success"

            else:
                response_data["message"] = "vide"

    return HttpResponse(json.dumps(response_data), content_type="application/json")


@csrf_exempt
def del_discution(request):
    response_data = {'message': "requette invalide", 'etat': False}

    if request.method == "POST":
        form = dict()
        try:
            form = json.loads(request.body.decode("utf-8"))
        except:
            ...

        if "id" in form:
            id = form.get("id")

            discution = Discution.objects.all().filter(id=id).first()

            if discution:
                discution.delete()
                response_data["etat"] = True
                response_data["message"] = "success"
            else:
                response_data["message"] = "message non trouver"

    return HttpResponse(json.dumps(response_data), content_type="application/json")


@csrf_exempt
def set_discution(request):
    response_data = {'message': "requette invalide", 'etat': False}

    if request.method == "POST":
        form = dict()
        try:
            form = json.loads(request.body.decode("utf-8"))
        except:
            ...

        if "id" in form and "lue" in form:

            id = form.get("id")
            lue = form.get("lue")

            discution = Discution.objects.all().filter(id=id).first()

            if discution:
                discution.lue = lue
                discution.save()
                response_data["etat"] = True
                response_data["message"] = "success"
            else:
                response_data["message"] = "message non trouver"

    return HttpResponse(json.dumps(response_data), content_type="application/json")


@csrf_exempt
def add_temoignages(request):
    response_data = {'message': "requette invalide", 'etat': False}

    if request.method == "POST":
        form = dict()
        try:
            form = json.loads(request.body.decode("utf-8"))
        except:
            ...
        if "apprenant_id" in form and "formation_slug" in form and "message" in form:
            apprenant_id = form.get("apprenant_id")
            formation_slug = form.get("formation_slug")
            message = form.get("message")

            # apprenant

            apprenant = Utilisateur.objects.all().filter(id=apprenant_id).first()

            if apprenant:
                # formation
                formation = Formation.objects.all().filter(slug=formation_slug).first()

                if formation:
                    # verifier si l'apprenant suit cette formation ou pas
                    tmp_cour = Cour.objects.all().filter(apprenant=apprenant, formation=formation)

                    if len(tmp_cour) > 0:
                        new_temoignage = Temoignage(apprenant=apprenant, formation=formation, message=message)
                        new_temoignage.save()

                        response_data["etat"] = True
                        response_data["message"] = "success"
                        response_data["id"] = new_temoignage.id
                    else:
                        response_data["message"] = "cet apprenant ne suit pas cette formation"
                else:
                    response_data["message"] = "formation non trouver"
            else:
                response_data["message"] = "apprenant non trouver"

    return HttpResponse(json.dumps(response_data), content_type="application/json")


@csrf_exempt
def get_temoignages(request):
    response_data = {'message': "requette invalide", 'etat': False}

    if request.method == "POST":
        form = dict()
        try:
            form = json.loads(request.body.decode("utf-8"))
        except:
            ...
        if "moderer" in form and "actif" in form and "apprenant_id" in form or "formation_slug" in form:

            moderer = form.get("moderer")
            actif = form.get("actif")

            all_temoignages = Temoignage.objects.all().filter(actif=actif, moderer=moderer)

            filtrer = False

            if "apprenant_id" in form:
                apprenant_id = form.get("apprenant_id")

                apprenant = Utilisateur.objects.all().filter(id=apprenant_id).first()

                if apprenant:
                    all_temoignages = all_temoignages.filter(apprenant=apprenant)
                    filtrer = True
                else:
                    response_data["message"] = "apprenant non trouver"

            else:
                formation_slug = form.get("formation_slug")
                formation = Formation.objects.all().filter(slug=formation_slug).first()

                if formation:
                    all_temoignages = all_temoignages.filter(formation=formation)
                    filtrer = True
                else:
                    response_data["message"] = "formation non trouver"

            if filtrer:
                temoignages = list()

                for t in all_temoignages:
                    temoignages.append(
                        {
                            "message": t.message,
                            "vue": t.vue,
                            "moderer": t.moderer,
                            "actif": t.actif,
                            "date": str(t.date),
                        }
                    )

                if len(temoignages) > 0:
                    response_data["etat"] = True
                    response_data["message"] = "success"
                    response_data["donnee"] = temoignages

    return HttpResponse(json.dumps(response_data), content_type="application/json")


@csrf_exempt
def get_temoignages_sans_m(request):
    response_data = {'message': "requette invalide", 'etat': False}

    if request.method == "POST":
        form = dict()
        try:
            form = json.loads(request.body.decode("utf-8"))
        except:
            ...
        if "apprenant_id" in form or "formation_slug" in form:

            all_temoignages = Temoignage.objects.all()

            filtrer = False

            if "apprenant_id" in form:
                apprenant_id = form.get("apprenant_id")

                apprenant = Utilisateur.objects.all().filter(id=apprenant_id).first()

                if apprenant:
                    all_temoignages = all_temoignages.filter(apprenant=apprenant)
                    filtrer = True
                else:
                    response_data["message"] = "apprenant non trouver"

            else:
                formation_slug = form.get("formation_slug")
                formation = Formation.objects.all().filter(slug=formation_slug).first()

                if formation:
                    all_temoignages = all_temoignages.filter(formation=formation)
                    filtrer = True
                else:
                    response_data["message"] = "formation non trouver"

            if filtrer:
                temoignages = list()

                for t in all_temoignages:
                    temoignages.append(
                        {
                            "apprenant_id": t.apprenant.id,
                            "apprenant_last_name": t.apprenant.last_name,
                            "apprenant_first_name": t.apprenant.first_name,
                            "apprenant_avatar": t.apprenant.avatar.url if t.apprenant.avatar else None,
                            "message": t.message,
                            "vue": t.vue,
                            "moderer": t.moderer,
                            "actif": t.actif,
                            "date": str(t.date),
                        }
                    )

                if len(temoignages) > 0:
                    response_data["etat"] = True
                    response_data["message"] = "success"
                    response_data["donnee"] = temoignages

    return HttpResponse(json.dumps(response_data), content_type="application/json")


@csrf_exempt
def set_temoignages(request):
    response_data = {'message': "requette invalide", 'etat': False}

    if request.method == "POST":
        form = dict()
        try:
            form = json.loads(request.body.decode("utf-8"))
        except:
            ...

        if "id" in form:
            id = form.get("id")
            temoignage = Temoignage.objects.all().filter(id=id).first()

            if temoignage:
                modifier = False
                if "message" in form:
                    message = form.get("message")

                    temoignage.message = message
                    modifier = True

                if "vue" in form:
                    vue = form.get("vue")

                    temoignage.vue = vue
                    modifier = True

                if "moderer" in form:
                    moderer = form.get("moderer")

                    temoignage.moderer = moderer

                    modifier = True

                if "actif" in form:
                    actif = form.get("actif")
                    temoignage.actif = actif

                    modifier = True

                if modifier:
                    temoignage.save()
                    response_data["etat"] = True
                    response_data["message"] = "success"

            else:
                response_data["message"] = "temoignage non trouver"

    return HttpResponse(json.dumps(response_data), content_type="application/json")


@csrf_exempt
def del_temoignages(request):
    response_data = {'message': "requette invalide", 'etat': False}

    if request.method == "POST":
        form = dict()
        try:
            form = json.loads(request.body.decode("utf-8"))
        except:
            ...

        if "id" in form:
            id = form.get("id")
            temoignage = Temoignage.objects.all().filter(id=id).first()

            if temoignage:

                temoignage.delete()

                response_data["etat"] = True
                response_data["message"] = "success"

            else:
                response_data["message"] = "temoignage non trouver"

    return HttpResponse(json.dumps(response_data), content_type="application/json")


"""
Cour
"""


@csrf_exempt
def set_cour(request):
    response_data = {'message': "requette invalide", 'etat': False}

    if request.method == "POST":
        form = dict()
        try:
            form = json.loads(request.body.decode("utf-8"))
        except:
            ...

        if "id" in form:
            id = form.get("id")

            cour = Cour.objects.all().filter(id=id).first()

            if cour:
                modifier = False

                if "montant" in form:
                    montant = form.get("montant")
                    cour.montant = montant
                    modifier = True

                if "progression" in form:
                    progression = form.get("progression")

                    cour.progression = progression
                    modifier = True

                if "terminer" in form:
                    terminer = form.get("terminer")
                    cour.terminer = terminer
                    modifier = True

                if modifier:
                    cour.save()
                    response_data["etat"] = True
                    response_data["message"] = "success"
            else:
                response_data["etat"] = "cour non trouver"

    return HttpResponse(json.dumps(response_data), content_type="application/json")


@csrf_exempt
def get_cour(request):
    response_data = {'message': "requette invalide", 'etat': False}

    if request.method == "POST":
        form = dict()
        try:
            form = json.loads(request.body.decode("utf-8"))
        except:
            ...
        all_cour = Cour.objects.all()
        filtrer = False

        if "apprenant_id":
            apprenant_id = form.get("apprenant_id")
            apprenant = Utilisateur.objects.all().filter(id=apprenant_id).first()
            if apprenant:
                all_cour = all_cour.filter(apprenant=apprenant)
                filtrer = True
            else:
                response_data["message"] = "apprenant non trouver"

        if "formation_slug" in form:
            formation_slug = form.get("formation_slug")

            formation = Formation.objects.all().filter(slug=formation_slug).first()

            if formation:
                all_cour = all_cour.filter(formation=formation)
                filtrer = True
            else:
                response_data["message"] = "formation non trouver"

        if "terminer" in form:
            terminer = form.get("terminer")

            all_cour = all_cour.filter(terminer=terminer)
            filtrer = True

        if filtrer:
            cours = list()

            for c in all_cour:
                cours.append(
                    {
                        "id": c.id,
                        "apprenant_id": c.apprenant.id,
                        "apprenant_first_name": c.apprenant.first_name,
                        "apprenant_avatar": c.apprenant.avatar.url if c.apprenant.avatar else None,
                        "apprenant_last_name": c.apprenant.last_name,
                        "formation_nom": c.formation.nom,
                        "formation_slug": c.formation.slug,
                        "montant": c.montant,
                        "date": str(c.date),
                        "progression": c.progression,
                        "terminer": c.terminer,
                    }
                )

            if len(cours) > 0:
                response_data["etat"] = True
                response_data["message"] = "success"
                response_data["donnee"] = cours
            else:
                response_data["message"] = "vide"

    return HttpResponse(json.dumps(response_data), content_type="application/json")


@csrf_exempt
def del_cour(request):
    response_data = {'message': "requette invalide", 'etat': False}

    if request.method == "POST":
        form = dict()
        try:
            form = json.loads(request.body.decode("utf-8"))
        except:
            ...

        if "id" in form:
            id = form.get("id")

            cour = Cour.objects.all().filter(id=id).first()

            if cour:
                cour.delete()
                response_data["message"] = "success"
                response_data["etat"] = True
            else:
                response_data["message"] = "cour non trouver"

    return HttpResponse(json.dumps(response_data), content_type="application/json")


"""
Suive
"""


@csrf_exempt
def add_suive(request):
    response_data = {'message': "requette invalide", 'etat': False}

    if request.method == "POST":
        form = dict()
        try:
            form = json.loads(request.body.decode("utf-8"))
        except:
            ...

        if "apprenant_id" in form and "souscategorie_id" in form:

            apprenant_id = form.get("apprenant_id")
            souscategorie_id = form.get("souscategorie_id")

            # formation
            souscategorie = SousCategorie.objects.all().filter(id=souscategorie_id).first()

            if souscategorie:
                # apprenant
                apprenant = Utilisateur.objects.all().filter(id=apprenant_id).first()

                if apprenant:

                    new_suive = Suive(apprenant=apprenant, souscategorie=souscategorie)
                    new_suive.save()

                    response_data["etat"] = True
                    response_data["message"] = "success"
                    response_data["id"] = new_suive.id
                else:
                    response_data["message"] = "apprenant non trouver"
            else:
                response_data["message"] = "souscategorie non trouver"

    return HttpResponse(json.dumps(response_data), content_type="application/json")


@csrf_exempt
def set_suive(request):
    response_data = {'message': "requette invalide", 'etat': False}

    if request.method == "POST":
        form = dict()
        try:
            form = json.loads(request.body.decode("utf-8"))
        except:
            ...

        if "id" in form:
            id = form.get("id")

            suive = Suive.objects.all().filter(id=id).first()

            if suive:
                modifier = False

                if "terminer" in form:
                    terminer = form.get("terminer")
                    suive.terminer = terminer
                    modifier = True

                if modifier:
                    suive.save()
                    response_data["etat"] = True
                    response_data["message"] = "success"
            else:
                response_data["etat"] = "suive non trouver"

    return HttpResponse(json.dumps(response_data), content_type="application/json")


@csrf_exempt
def get_suive(request):
    response_data = {'message': "requette invalide", 'etat': False}

    if request.method == "POST":
        form = dict()
        try:
            form = json.loads(request.body.decode("utf-8"))
        except:
            ...
        all_suive = Suive.objects.all()
        filtrer = False

        if "apprenant_id" in form:
            apprenant_id = form.get("apprenant_id")
            apprenant = Utilisateur.objects.all().filter(id=apprenant_id).first()
            if apprenant:
                all_suive = all_suive.filter(apprenant=apprenant)
                filtrer = True
            else:
                response_data["message"] = "apprenant non trouver"

        if "souscategorie_id" in form:
            souscategorie_id = form.get("souscategorie_id")

            souscategorie = SousCategorie.objects.all().filter(slug=souscategorie_id).first()

            if souscategorie:
                all_suive = all_suive.filter(souscategorie=souscategorie)
                filtrer = True
            else:
                response_data["message"] = "souscategorie non trouver"

        if "terminer" in form:
            terminer = form.get("terminer")

            all_suive = all_suive.filter(terminer=terminer)
            filtrer = True

        if filtrer:
            suives = list()

            for c in all_suive:
                suives.append(
                    {
                        "id": c.id,
                        "apprenant_id": c.apprenant.id,
                        "apprenant_first_name": c.apprenant.first_name,
                        "apprenant_avatar": c.apprenant.avatar.url if c.apprenant.avatar else None,
                        "apprenant_last_name": c.apprenant.last_name,
                        "souscategorie_nom": c.souscategorie.nom,
                        "souscategorie_id": c.souscategorie.id,
                        "image": c.souscategorie.image.url if c.souscategorie.image else None,
                        "formation_id": c.souscategorie.id,
                        "date": str(c.date),
                        "terminer": c.terminer,
                    }
                )

            if len(suives) > 0:
                response_data["etat"] = True
                response_data["message"] = "success"
                response_data["donnee"] = suives
            else:
                response_data["message"] = "vide"

    return HttpResponse(json.dumps(response_data), content_type="application/json")


@csrf_exempt
def del_suive(request):
    response_data = {'message': "requette invalide", 'etat': False}

    if request.method == "POST":
        form = dict()
        try:
            form = json.loads(request.body.decode("utf-8"))
        except:
            ...

        if "id" in form:
            id = form.get("id")

            suive = Suive.objects.all().filter(id=id).first()

            if suive:
                suive.delete()
                response_data["message"] = "success"
                response_data["etat"] = True
            else:
                response_data["message"] = "cour non trouver"

    return HttpResponse(json.dumps(response_data), content_type="application/json")


"""
Participer
"""


@csrf_exempt
def add_participer(request):
    response_data = {'message': "requette invalide", 'etat': False}

    if request.method == "POST":
        form = dict()
        try:
            form = json.loads(request.body.decode("utf-8"))
        except:
            ...

        if "apprenant_id" in form and "qcm_id" in form:

            apprenant_id = form.get("apprenant_id")
            qcm_id = form.get("qcm_id")

            # formation
            qcm = Qcm.objects.all().filter(id=qcm_id).first()

            if qcm:
                # apprenant
                apprenant = Utilisateur.objects.all().filter(id=apprenant_id).first()

                if apprenant:

                    new_participer = Participer(apprenant=apprenant, qcm=qcm)
                    new_participer.save()

                    response_data["etat"] = True
                    response_data["message"] = "success"
                    response_data["id"] = new_participer.id
                else:
                    response_data["message"] = "apprenant non trouver"
            else:
                response_data["message"] = "qcm non trouver"

    return HttpResponse(json.dumps(response_data), content_type="application/json")


@csrf_exempt
def set_participer(request):
    response_data = {'message': "requette invalide", 'etat': False}

    if request.method == "POST":
        form = dict()
        try:
            form = json.loads(request.body.decode("utf-8"))
        except:
            ...

        if "id" in form:
            id = form.get("id")

            participer = Participer.objects.all().filter(id=id).first()

            if participer:
                modifier = False

                if "point" in form:
                    point = form.get("point")
                    participer.point = point
                    modifier = True

                if modifier:
                    participer.save()
                    response_data["etat"] = True
                    response_data["message"] = "success"
            else:
                response_data["etat"] = "suive non trouver"

    return HttpResponse(json.dumps(response_data), content_type="application/json")


@csrf_exempt
def get_participer(request):
    response_data = {'message': "requette invalide", 'etat': False}

    if request.method == "POST":
        form = dict()
        try:
            form = json.loads(request.body.decode("utf-8"))
        except:
            ...
        all_participer = Participer.objects.all()
        filtrer = False

        if "apprenant_id" in form:
            apprenant_id = form.get("apprenant_id")
            apprenant = Utilisateur.objects.all().filter(id=apprenant_id).first()
            if apprenant:
                all_participer = all_participer.filter(apprenant=apprenant)
                filtrer = True
            else:
                response_data["message"] = "apprenant non trouver"

        if "qcm_id" in form:
            qcm_id = form.get("qcm_id")

            qcm = Qcm.objects.all().filter(slug=qcm_id).first()

            if qcm:
                all_participer = all_participer.filter(qcm=qcm)
                filtrer = True
            else:
                response_data["message"] = "qcm non trouver"

        if "terminer" in form:
            terminer = form.get("terminer")

            all_participer = all_participer.filter(terminer=terminer)
            filtrer = True

        if filtrer:
            suives = list()

            for c in all_participer:
                suives.append(
                    {
                        "id": c.id,
                        "apprenant_id": c.apprenant.id,
                        "apprenant_first_name": c.apprenant.first_name,
                        "apprenant_avatar": c.apprenant.avatar.url if c.apprenant.avatar else None,
                        "apprenant_last_name": c.apprenant.last_name,
                        "souscategorie_nom": c.souscategorie.nom,
                        "souscategorie_id": c.souscategorie.id,
                        "image": c.souscategorie.image.url if c.souscategorie.image else None,
                        "formation_id": c.souscategorie.id,
                        "date": str(c.date),
                        "terminer": c.terminer,
                    }
                )

            if len(suives) > 0:
                response_data["etat"] = True
                response_data["message"] = "success"
                response_data["donnee"] = suives
            else:
                response_data["message"] = "vide"

    return HttpResponse(json.dumps(response_data), content_type="application/json")


@csrf_exempt
def participer_get_all(request):
    response_data = {'message': "requette invalide", 'etat': False}

    participer = Participer.objects.all()

    all_participer = list()

    for ex in participer:
        all_participer.append(
            {
                "id": ex.id,
                "point": ex.point,
                "apprenant_id": ex.apprenant.id,
                "apprenant_id": ex.apprenant.id,
                "apprenant_nom": ex.apprenant.first_name,
                "apprenant_prenom": ex.apprenant.last_name,
                "qcm_id": ex.qcm.id,
                "qcm_form": ex.qcm.formation_id,
                "qcm_nom": ex.qcm.nom,
                "date": str(ex.date)
            }
        )

    if len(all_participer) > 0:
        response_data["etat"] = True
        response_data["message"] = "success"
        response_data["donnee"] = all_participer
    else:
        response_data["message"] = "vide"

    return HttpResponse(json.dumps(response_data), content_type="application/json")


@csrf_exempt
def del_participer(request):
    response_data = {'message': "requette invalide", 'etat': False}

    if request.method == "POST":
        form = dict()
        try:
            form = json.loads(request.body.decode("utf-8"))
        except:
            ...

        if "id" in form:
            id = form.get("id")

            participer = Participer.objects.all().filter(id=id).first()

            if participer:
                participer.delete()
                response_data["message"] = "success"
                response_data["etat"] = True
            else:
                response_data["message"] = "participation non trouver"

    return HttpResponse(json.dumps(response_data), content_type="application/json")


"""
VideoVue
"""


@csrf_exempt
def add_video_vue(request):
    response_data = {'message': "requette invalide", 'etat': False}

    if request.method == "POST":
        form = dict()
        try:
            form = json.loads(request.body.decode("utf-8"))
        except:
            ...

        if "video_id" in form and "cour_id" in form:

            cour_id = form.get("cour_id")
            video_id = form.get("video_id")

            # recup le cour
            cour = Cour.objects.all().filter(id=cour_id).first()

            if cour:

                # recup la video
                video = Video.objects.all().filter(id=video_id).first()

                if video:
                    new_video_vue = VideoVue(video=video, cour=cour)
                    new_video_vue.save()

                    response_data["message"] = "success"
                    response_data["etat"] = True
                    response_data["id"] = new_video_vue.id

                else:
                    response_data["message"] = "video non trouver"
            else:
                response_data["message"] = "cour non trouver"

    return HttpResponse(json.dumps(response_data), content_type="application/json")


@csrf_exempt
def get_video_vue(request):
    response_data = {'message': "requette invalide", 'etat': False}

    if request.method == "POST":
        form = dict()
        try:
            form = json.loads(request.body.decode("utf-8"))
        except:
            ...

        if "video_id" in form and "cour_id" in form:

            cour_id = form.get("cour_id")
            video_id = form.get("video_id")

            # recup le cour
            cour = Cour.objects.all().filter(id=cour_id).first()

            if cour:
                all_video_vue = VideoVue.objects.all().filter(cour=cour)

                video_vues = list()

                for v in all_video_vue:
                    video_vues.append(
                        {
                            "video_id": v.video.id,
                            "cour_id": v.cour.id,
                            "date": str(v.date)
                        }
                    )

                if len(video_vues):
                    response_data["donnee"] = video_vues
                    response_data["etat"] = True
                    response_data["message"] = "success"
                else:
                    response_data["message"] = "vide"


            else:
                response_data["message"] = "cour non trouver"
    return HttpResponse(json.dumps(response_data), content_type="application/json")


@csrf_exempt
def del_video_vue(request):
    response_data = {'message': "requette invalide", 'etat': False}

    if request.method == "POST":
        form = dict()
        try:
            form = json.loads(request.body.decode("utf-8"))
        except:
            ...

        if "id" in form:
            id = form.get("id")

            video_vue = VideoVue.objects.all().filter(id=id).first()
            if video_vue:
                video_vue.delete()
                response_data["etat"] = True
                response_data["message"] = "success"
            else:
                response_data["message"] = "video vue non trouver"

    return HttpResponse(json.dumps(response_data), content_type="application/json")


"""
Video
"""


@csrf_exempt
@xframe_options_exempt
def add_video(request, chapitre_id):
    if request.method == "POST":
        form = request.POST

        if True:
            nom = form.get("nom")
            duree = form.get("duree")
            video = request.FILES.get('video')
            ordre = form.get("ordre")
            # chapitre_id = form.get("chapitre_id")

            # print("video = ")
            # print(video)
            # chapitre
            chapitre = Chapitre.objects.all().filter(id=chapitre_id).first()

            if chapitre:
                ...
                # video = base64_to_image(video_64)

                new_Video = Video(nom=nom, duree=duree, video=video, ordre=ordre, chapitre=chapitre)

                new_Video.save()

                # response_data["etat"] = True
                # response_data["message"] = "success"
                # response_data["id"] = new_Video.id
                return render(request, "formation/add_video_merci.html", context={"chapitre_id": chapitre_id})
            else:
                return render(request, "formation/add_video_erreur.html", context={"chapitre_id": chapitre_id})

    return render(request, "formation/add_video.html", context={"chapitre_id": chapitre_id})


@csrf_exempt
def get_video(request):
    response_data = {'message': "requette invalide", 'etat': False}

    if request.method == "POST":
        form = dict()
        try:
            form = json.loads(request.body.decode("utf-8"))
        except:
            ...

        if "chapitre_id" in form:
            chapitre_id = form.get("chapitre_id")
            chapitre = Chapitre.objects.all().filter(id=chapitre_id).first()

            if chapitre:
                all_vdieo = Video.objects.all().filter(chapitre=chapitre).order_by("ordre")

                videos = list()

                for v in all_vdieo:
                    videos.append(
                        {
                            "nom": v.nom,
                            "id": v.id,
                            "duree": v.duree,
                            "video_url": v.video.url if v.video else None,
                            "chapitre_id": v.chapitre.id,
                            "ordre": v.ordre,
                        }
                    )

                if len(videos) > 0:
                    response_data["etat"] = True
                    response_data["message"] = "success"
                    response_data["donnee"] = videos
                else:
                    response_data["message"] = "vide"
            else:
                response_data["message"] = "chapitre non trouver"

    return HttpResponse(json.dumps(response_data), content_type="application/json")


@csrf_exempt
def get_video_un(request, id):
    response_data = {'message': "requette invalide", 'etat': False}
    video = Video.objects.all().filter(id=id).first()

    if video:
        categorie_data = {
            "id": video.id,
            "nom": video.nom,
            "duree": video.duree,
            "ordre": video.ordre,
            "video": video.video.url if video.video else None,
        }

        response_data["etat"] = True
        response_data["donnee"] = categorie_data
        response_data["message"] = "success"
    else:
        response_data["message"] = "video non trouver"

    return HttpResponse(json.dumps(response_data), content_type="application/json")



@csrf_exempt
def del_video(request):
    response_data = {'message': "requette invalide", 'etat': False}

    if request.method == "POST":
        form = dict()
        try:
            form = json.loads(request.body.decode("utf-8"))
        except:
            ...

        if "id" in form:
            id = form.get("id")
            video = Video.objects.all().filter(id=id).first()

            if video:
                if video.video:
                    import os
                    try:
                        os.remove(video.video.path)
                    except:
                        ...
                    video.delete()
                    response_data["etat"] = True
                    response_data["message"] = "success"
            else:
                response_data["message"] = "video non trouver"
    return HttpResponse(json.dumps(response_data), content_type="application/json")


@csrf_exempt
def set_video(request):
    response_data = {'message': "requette invalide", 'etat': False}

    if request.method == "POST":
        form = dict()
        try:
            form = json.loads(request.body.decode("utf-8"))
        except:
            ...

        if "id" in form:
            id = form.get("id")
            video = Video.objects.all().filter(id=id).first()

            modifier = False

            if "nom" in form:
                nom = form.get("nom")
                video.nom = nom
                modifier = True

            if "duree" in form:
                duree = form.get("duree")
                video.duree = duree
                modifier = True

            if "ordre" in form:
                ordre = form.get("ordre")
                video.ordre = ordre
                modifier = True

            if "chapitre_id" in form:
                chapitre_id = form.get("chapitre_id")

                chapitre = Chapitre.objects.all().filter(id=chapitre_id).first()

                if chapitre:
                    video.chapitre = chapitre
                    modifier = True
                else:
                    response_data["message"] = "chapitre non trouver"

            if modifier:
                video.save()
                response_data["etat"] = True
                response_data["message"] = "success"

        else:
            response_data["message"] = "video non trouver"
    return HttpResponse(json.dumps(response_data), content_type="application/json")


@csrf_exempt
def add_seancetravail(request):
    response_data = {'message': "requette invalide", 'etat': False}

    if request.method == "POST":
        form = dict()
        try:
            form = json.loads(request.body.decode("utf-8"))
        except:
            ...

        if "apprenant_id" in form and "formation_slug" in form and "nom" in form and "lien_de_la_reunion" in form and "date_de_la_reunion" in form:
            apprenant_id = form.get("apprenant_id")
            formation_slug = form.get("formation_slug")
            nom = form.get("nom")
            lien_de_la_reunion = form.get("lien_de_la_reunion")
            date_de_la_reunion = form.get("date_de_la_reunion")

            # formation
            formation = Formation.objects.all().filter(slug=formation_slug).first()

            if formation:
                # apprenant
                apprenant = Utilisateur.objects.all().filter(id=apprenant_id).first()
                if apprenant:

                    new_seancetravail = SeanceTravail(
                        nom=nom,
                        apprenant=apprenant,
                        formation=formation,
                        lien_de_la_reunion=lien_de_la_reunion,
                        date_de_la_reunion=date_de_la_reunion
                    )

                    new_seancetravail.save()

                    response_data["etat"] = True
                    response_data["id"] = new_seancetravail.id
                    response_data["message"] = "success"
                else:
                    response_data["message"] = "utilisateur non trouver"
            else:
                response_data["message"] = "formation non trouver"

    return HttpResponse(json.dumps(response_data), content_type="application/json")


@csrf_exempt
def set_seancetravail(request):
    response_data = {'message': "requette invalide", 'etat': False}

    if request.method == "POST":
        form = dict()
        try:
            form = json.loads(request.body.decode("utf-8"))
        except:
            ...

        if "id" in form:
            id = form.get("id")
            seancetravail = SeanceTravail.objects.all().filter(id=id).first()

            if seancetravail:
                modifier = False

                if "nom" in form:
                    nom = form.get("nom")

                    seancetravail.nom = nom
                    modifier = True

                if "apprenant_id" in form:
                    apprenant_id = form.get("apprenant_id")

                    apprenant = Utilisateur.objects.all().filter(id=apprenant_id).first()
                    if apprenant:
                        seancetravail.apprenant = apprenant
                        modifier = True
                    else:
                        response_data["message"] = "apprenant non trouver"

                if "formation_slug" in form:
                    formation_slug = form.get("formation_slug")
                    formation = Formation.objects.all().filter(slug=formation_slug).first()

                    if formation:
                        seancetravail.formation = formation
                        modifier = True
                    else:
                        response_data["message"] = "formatino non trouver"
                if "lien_de_la_reunion" in form:
                    lien_de_la_reunion = form.get("lien_de_la_reunion")

                    seancetravail.lien_de_la_reunion = lien_de_la_reunion
                    modifier = True

                if "confirmer_par_apprenant":
                    confirmer_par_apprenant = form.get("confirmer_par_apprenant")

                    seancetravail.confirmer_par_apprenant = confirmer_par_apprenant
                    modifier = True

                if "confirmer_par_instructeur" in form:
                    confirmer_par_instructeur = form.get("confirmer_par_instructeur")

                    seancetravail.confirmer_par_instructeur = confirmer_par_instructeur
                    modifier = True

                if "date_de_la_reunion" in form:
                    date_de_la_reunion = form.get("date_de_la_reunion")

                    seancetravail.date_de_la_reunion = date_de_la_reunion

                    modifier = True

                if modifier:
                    response_data["etat"] = True
                    response_data["message"] = "success"

            else:
                response_data["message"] = "seance de travail non trouver"

    return HttpResponse(json.dumps(response_data), content_type="application/json")


@csrf_exempt
def del_seancetravail(request):
    response_data = {'message': "requette invalide", 'etat': False}

    if request.method == "POST":
        form = dict()
        try:
            form = json.loads(request.body.decode("utf-8"))
        except:
            ...

        if "id" in form:
            id = form.get("id")
            seancetravail = SeanceTravail.objects.all().filter(id=id).first()

            if seancetravail:
                seancetravail.delete()
                response_data["etat"] = True
                response_data["message"] = "success"
            else:
                response_data["message"] = "seance de travail non trouver"

    return HttpResponse(json.dumps(response_data), content_type="application/json")


@csrf_exempt
def get_seancetravail(request):
    response_data = {'message': "requette invalide", 'etat': False}

    if request.method == "POST":
        form = dict()
        try:
            form = json.loads(request.body.decode("utf-8"))
        except:
            ...

        if "apprenant_id" in form and "formation_slug":
            formation_slug = form.get("formation_slug")
            apprenant_id = form.get("apprenant_id")

            formation = Formation.objects.all().filter(slug=formation_slug).first()
            if formation:
                apprenant = Utilisateur.objects.all().filter(id=apprenant_id).first()
                if apprenant:
                    all_seance = SeanceTravail.objects.all().filter(formation=formation, apprenant=apprenant)

                    seances = list()

                    for s in all_seance:
                        seances.append(
                            {
                                "nom": s.nom,
                                "id": s.id,
                                "lien_de_la_reunion": s.lien_de_la_reunion,
                                "confirmer_par_apprenant": s.confirmer_par_apprenant,
                                "confirmer_par_instructeur": s.confirmer_par_instructeur,
                                "date": str(s.date),
                                "date_de_la_reunion": str(s.date_de_la_reunion),
                                "apprenant_id": s.apprenant.id,
                                "apprenant_first_name": s.apprenant.first_name,
                                "apprenant_last_name": s.apprenant.last_name,
                                "apprenant_username": s.apprenant.username,

                                "formation.slug": s.formation.slug,
                                "formation.nom": s.formation.nom,
                            }
                        )
                    if len(seances) > 0:
                        response_data["message"] = "succes"
                        response_data["etat"] = True
                        response_data["donnee"] = seances
                    else:
                        response_data["message"] = "vide"
                else:
                    response_data["message"] = "apprenant non trouver"
            else:
                response_data["message"] = "formation non trouver"

    return HttpResponse(json.dumps(response_data), content_type="application/json")


@csrf_exempt
def get_all_seancetravail(request):
    response_data = {'message': "requette invalide", 'etat': False}

    all_seance = SeanceTravail.objects.all()

    seances = list()

    for s in all_seance:
        seances.append(
            {
                "nom": s.nom,
                "id": s.id,
                "lien_de_la_reunion": s.lien_de_la_reunion,
                "confirmer_par_apprenant": s.confirmer_par_apprenant,
                "confirmer_par_instructeur": s.confirmer_par_instructeur,
                "date": str(s.date),
                "date_de_la_reunion": str(s.date_de_la_reunion),
                "apprenant_id": s.apprenant.id,
                "apprenant_first_name": s.apprenant.first_name,
                "apprenant_last_name": s.apprenant.last_name,
                "apprenant_username": s.apprenant.username,

                "formation.slug": s.formation.slug,
                "formation.nom": s.formation.nom,
            }
        )
    if len(seances) > 0:
        response_data["message"] = "succes"
        response_data["etat"] = True
        response_data["donnee"] = seances
    else:
        response_data["message"] = "vide"

    return HttpResponse(json.dumps(response_data), content_type="application/json")


@csrf_exempt
def get_detaille_seancetravail(request, id):
    response_data = {'message': "requette invalide", 'etat': False}

    seance = SeanceTravail.objects.all().filter(id=id).first()

    if seance:
        seance_data = {
            "nom": seance.nom,
            "id": seance.id,
            "lien_de_la_reunion": seance.lien_de_la_reunion,
            "confirmer_par_apprenant": seance.confirmer_par_apprenant,
            "confirmer_par_instructeur": seance.confirmer_par_instructeur,
            "date": str(seance.date),
            "date_de_la_reunion": str(seance.date_de_la_reunion),
            "apprenant_id": seance.apprenant.id,
            "apprenant_first_name": seance.apprenant.first_name,
            "apprenant_last_name": seance.apprenant.last_name,
            "apprenant_username": seance.apprenant.username,

            "formation.slug": seance.formation.slug,
            "formation.nom": seance.formation.nom,
        }
        response_data["etat"] = True
        response_data["message"] = "success"
        response_data["donnee"] = seance_data
    else:
        response_data["message"] = "seance de travail non trouver"

    return HttpResponse(json.dumps(response_data), content_type="application/json")


"""
************************************************************
Quiz
************************************************************
"""


@csrf_exempt
def add_qcm(request):
    response_data = {'message': "requette invalide", 'etat': False}

    if request.method == "POST":
        form = dict()
        try:
            form = json.loads(request.body.decode("utf-8"))
        except:
            ...

        if "nom" in form and "description" in form and "duree" in form and "formation_slug" in form:
            nom = form.get("nom")
            description = form.get("description")
            duree = form.get("duree")
            formation_slug = form.get("formation_slug")

            # formation
            formation = Formation.objects.all().filter(slug=formation_slug).first()

            if formation:
                new_qcm = Qcm(nom=nom,
                              description=description,
                              duree=duree,
                              formation=formation)
                new_qcm.save()

                response_data["etat"] = True
                response_data["id"] = new_qcm.id
                response_data["message"] = "success"

            else:
                response_data["message"] = "formation non trouver"

    return HttpResponse(json.dumps(response_data), content_type="application/json")


@csrf_exempt
def del_qcm(request):
    response_data = {'message': "requette invalide", 'etat': False}

    if request.method == "POST":
        form = dict()
        try:
            form = json.loads(request.body.decode("utf-8"))
        except:
            ...

        if "id" in form:
            id = form.get("id")

            qcm = Qcm.objects.all().filter(id=id).first()

            if qcm:
                qcm.delete()
                response_data["etat"] = True
                response_data["message"] = "success"
            else:
                response_data["message"] = "qcm non trouver"

    return HttpResponse(json.dumps(response_data), content_type="application/json")


@csrf_exempt
def set_qcm(request):
    response_data = {'message': "requette invalide", 'etat': False}

    if request.method == "POST":
        form = dict()
        try:
            form = json.loads(request.body.decode("utf-8"))
        except:
            ...

        if "id" in form:
            id = form.get("id")

            qcm = Qcm.objects.all().filter(id=id).first()

            if qcm:

                modifier = False

                if "nom" in form:
                    nom = form.get("nom")
                    qcm.nom = nom
                    modifier = True

                if "description" in form:
                    description = form.get("description")
                    qcm.description = description
                    modifier = True

                if "duree" in form:
                    duree = form.get("duree")
                    qcm.duree = duree
                    modifier = True

                if modifier:
                    qcm.save()
                    response_data["etat"] = True
                    response_data["message"] = "success"
            else:
                response_data["message"] = "qcm non trouver"

    return HttpResponse(json.dumps(response_data), content_type="application/json")


@csrf_exempt
def get_qcm(request):
    response_data = {'message': "requette invalide", 'etat': False}

    if request.method == "POST":
        form = dict()
        try:
            form = json.loads(request.body.decode("utf-8"))
        except:
            ...

        if "formation_slug" in form:
            formation_slug = form.get("formation_slug")

            formation = Formation.objects.all().filter(slug=formation_slug).first()

            if formation:
                all_qcm = Qcm.objects.all().filter(formation=formation)

                qcms = list()

                for q in all_qcm:
                    qcms.append(
                        {
                            "nom": q.nom,
                            "id": q.id,
                            "description": q.description,
                            "duree": q.duree,
                            "formation_slug": q.formation.slug,
                            "formation_nom": q.formation.nom,
                            "point_total": q.point_total,
                            "date": str(q.date)
                        }
                    )

                if len(qcms) > 0:
                    response_data["etat"] = True
                    response_data["message"] = "success"
                    response_data["donnee"] = qcms
                else:
                    response_data["message"] = "vide"
            else:
                response_data["message"] = "formation non trouver"

    return HttpResponse(json.dumps(response_data), content_type="application/json")


@csrf_exempt
def get_qcm_detail(request, id):
    response_data = {'message': "requette invalide", 'etat': False}

    qcm = Qcm.objects.all().filter(id=id).first()

    if qcm:
        qcm_data = {
            "nom": qcm.nom,
            "description": qcm.description,
            "duree": qcm.duree,
            "formation_slug": qcm.formation.slug,
            "formation_nom": qcm.formation.nom,
            "point_total": qcm.point_total,
            "date": str(qcm.date)
        }

        response_data["etat"] = True
        response_data["message"] = "success"
        response_data["donnee"] = qcm_data

    else:
        response_data["message"] = "qcm non trouver"

    return HttpResponse(json.dumps(response_data), content_type="application/json")


"""
*********************************************
Question
*********************************************
"""


@csrf_exempt
def add_qcm_question(request):
    response_data = {'message': "requette invalide", 'etat': False}

    if request.method == "POST":
        form = dict()
        try:
            form = json.loads(request.body.decode("utf-8"))
        except:
            ...

        if "question" in form and "qcm_id" in form and "point" in form:
            point = form.get("point")
            question = form.get("question")
            qcm_id = form.get("qcm_id")

            qcm = Qcm.objects.all().filter(id=qcm_id).first()

            if qcm:
                new_qcm = Question(point=point, question=question, qcm=qcm)
                new_qcm.save()
                response_data["etat"] = True
                response_data["message"] = "success"
                response_data["donnee"] = new_qcm.id
            else:
                response_data["message"] = "qcm non trouver"

    return HttpResponse(json.dumps(response_data), content_type="application/json")


@csrf_exempt
def del_qcm_question(request):
    response_data = {'message': "requette invalide", 'etat': False}

    if request.method == "POST":
        form = dict()
        try:
            form = json.loads(request.body.decode("utf-8"))
        except:
            ...

        if "id" in form:
            id = form.get("id")

            question = Question.objects.all().filter(id=id).first()

            if question:
                question.delete()
                response_data["etat"] = True
                response_data["message"] = "success"
            else:
                response_data["message"] = "question non trouver"

    return HttpResponse(json.dumps(response_data), content_type="application/json")


@csrf_exempt
def set_qcm_question(request):
    response_data = {'message': "requette invalide", 'etat': False}

    if request.method == "POST":
        form = dict()
        try:
            form = json.loads(request.body.decode("utf-8"))
        except:
            ...

        if "id" in form:
            id = form.get("id")

            question = Question.objects.all().filter(id=id).first()

            if question:
                modifier = False

                if "question" in form:
                    question_text = form.get("question")
                    question.question = question_text
                    modifier = True

                if "point" in form:
                    point = form.get("point")

                    question.point = point
                    modifier = True

                if modifier:
                    response_data["etat"] = True
                    response_data["message"] = "success"
            else:
                response_data["message"] = "question non trouver"

    return HttpResponse(json.dumps(response_data), content_type="application/json")


@csrf_exempt
def get_qcm_question(request):
    response_data = {'message': "requette invalide", 'etat': False}

    if request.method == "POST":
        form = dict()
        try:
            form = json.loads(request.body.decode("utf-8"))
        except:
            ...

        if "qcm_id" in form:
            qcm_id = form.get("qcm_id")

            qcm = Qcm.objects.all().filter(id=qcm_id).first()

            if qcm:
                all_question = list()
                for q in Question.objects.all().filter(qcm=qcm):
                    all_question.append(
                        {
                            "id": q.id,
                            "question": q.question,
                            "point": q.point,
                            "reponse": [
                                {
                                    "reponse": r.reponse,
                                    "correcte": r.correcte,

                                } for r in q.all_response
                            ],
                        }
                    )

                if len(all_question) > 0:
                    response_data["etat"] = True
                    response_data["message"] = "success"
                    response_data["donnee"] = all_question
                else:
                    response_data["message"] = "vide"
            else:
                response_data["message"] = "qcm non trouver"

    return HttpResponse(json.dumps(response_data), content_type="application/json")


"""
**************************************************
Reponse
**************************************************
"""


@csrf_exempt
def add_qcm_reponse(request):
    response_data = {'message': "requette invalide", 'etat': False}

    if request.method == "POST":
        form = dict()
        try:
            form = json.loads(request.body.decode("utf-8"))
        except:
            ...

        if "question_id" in form and "reponse" in form and "correcte" in form:
            correcte = form.get("correcte")
            question_id = form.get("question_id")
            reponse = form.get("reponse")

            # question
            question = Question.objects.all().filter(id=question_id).first()

            if question:
                new_response = Reponse(question=question, reponse=reponse, correcte=correcte)

                new_response.save()
                response_data["etat"] = True
                response_data["message"] = "success"
                response_data["id"] = new_response.id
            else:
                response_data["message"] = "question non trouver"

    return HttpResponse(json.dumps(response_data), content_type="application/json")


@csrf_exempt
def get_qcm_reponse(request):
    response_data = {'message': "requette invalide", 'etat': False}

    if request.method == "POST":
        form = dict()
        try:
            form = json.loads(request.body.decode("utf-8"))
        except:
            ...

        if "question_id" in form:
            question_id = form.get("question_id")

            question = Question.objects.all().filter(id=question_id).first()

            if question:
                all_reponse = list()

                for r in question.all_response:
                    all_reponse.append(
                        {
                            "id": r.id,
                            "reponse": r.reponse,
                            "correcte": r.correcte,
                        }
                    )

                if len(all_reponse) > 0:
                    response_data["etat"] = True
                    response_data["message"] = "success"
                    response_data["donnee"] = all_reponse

            else:
                response_data["message"] = "question non trouver"

    return HttpResponse(json.dumps(response_data), content_type="application/json")


@csrf_exempt
def get_all_qcm_reponse(request):
    response_data = {'message': "requette invalide", 'etat': False}
    reponse = Reponse.objects.all()

    all_reponse = list()
    for r in reponse:
        all_reponse.append(
            {
                "reponse": r.reponse,
                "correcte": r.correcte,
                "question_id": r.question_id,
            }
        )

    if len(all_reponse) > 0:
        response_data["etat"] = True
        response_data["message"] = "success"
        response_data["donnee"] = all_reponse

    else:
        response_data["message"] = "vide"

    return HttpResponse(json.dumps(response_data), content_type="application/json")


@csrf_exempt
def get_un_qcm_reponse(request, id):
    response_data = {'message': "requette invalide", 'etat': False}

    reponse = Reponse.objects.all().filter(id=id).first()

    if reponse:

        r = {
            "question_id": reponse.question.id,
            "reponse": reponse.reponse,
            "correcte": reponse.correcte,
        }

        response_data["etat"] = True
        response_data["message"] = "success"
        response_data["donnee"] = r

    else:
        response_data["message"] = "reponse non trouver"

    return HttpResponse(json.dumps(response_data), content_type="application/json")


@csrf_exempt
def set_qcm_reponse(request):
    response_data = {'message': "requette invalide", 'etat': False}

    if request.method == "POST":
        form = dict()
        try:
            form = json.loads(request.body.decode("utf-8"))
        except:
            ...

        if "id" in form:
            id = form.get("id")

            reponse = Reponse.objects.all().filter(id=id).first()

            if reponse:
                modifier = False

                if "reponse" in form:
                    reponse_text = form.get("reponse")

                    reponse.reponse = reponse_text

                    modifier = True

                if "correcte" in form:
                    correcte = form.get("correcte")
                    reponse.correcte = correcte
                    modifier = True

                if modifier:
                    response_data["etat"] = True
                    response_data["message"] = "success"
            else:
                response_data["message"] = "response non trouver"

    return HttpResponse(json.dumps(response_data), content_type="application/json")


@csrf_exempt
def del_qcm_reponse(request):
    response_data = {'message': "requette invalide", 'etat': False}

    if request.method == "POST":
        form = dict()
        try:
            form = json.loads(request.body.decode("utf-8"))
        except:
            ...

        if "id" in form:
            id = form.get("id")

            reponse = Reponse.objects.all().filter(id=id).first()

            if reponse:
                reponse.delete()
                response_data["etat"] = True
                response_data["message"] = "success"
            else:
                response_data["message"] = "reponse non trouver"

    return HttpResponse(json.dumps(response_data), content_type="application/json")


"""
********************************
examen
********************************
"""


@csrf_exempt
def examen_add(request):
    response_data = {'message': "requette invalide", 'etat': False}

    if request.method == "POST":
        form = dict()
        try:
            form = json.loads(request.body.decode("utf-8"))
        except:
            ...

        if "nom" in form and "apprenant_id" in form and "qcm_id" in form and "duree" in form and "point" in form:
            nom = form.get("nom")
            apprenant_id = form.get("apprenant_id")
            qcm_id = form.get("qcm_id")
            duree = form.get("duree")
            point = form.get("point")

            # apprenant
            apprenant = Utilisateur.objects.all().filter(id=apprenant_id).first()

            if apprenant:
                # qcm
                qcm = Qcm.objects.all().filter(id=qcm_id).first()
                if qcm:
                    new_examen = Examen(nom=nom, apprenant=apprenant, qcm=qcm, duree=duree, point=point)
                    new_examen.save()

                    response_data["etat"] = True
                    response_data["message"] = "success"
                    response_data["id"] = new_examen.id
                else:
                    response_data["message"] = "qcm non trouver"
            else:
                response_data["message"] = "utilisateur non trouver"

    return HttpResponse(json.dumps(response_data), content_type="application/json")


@csrf_exempt
def examen_set(request):
    response_data = {'message': "requette invalide", 'etat': False}

    if request.method == "POST":
        form = dict()
        try:
            form = json.loads(request.body.decode("utf-8"))
        except:
            ...

        if "id" in form:
            id = form.get("id")

            examen = Examen.objects.all().filter(id=id).first()
            if examen:
                modifier = False

                if "nom" in form:
                    nom = form.get("nom")
                    examen.nom = nom
                    modifier = True

                if "apprenant_id" in form:
                    apprenant_id = form.get("apprenant_id")

                    apprenant = Utilisateur.objects.all().filter(id=apprenant_id).first()

                    if apprenant:
                        examen.apprenant = apprenant
                        modifier = True
                    else:
                        response_data["message"] = "apprenant non trouver"
                if "qcm_id" in form:
                    qcm_id = form.get("qcm_id")

                    qcm = Qcm.objects.all().filter(id=qcm_id).first()

                    if qcm:
                        examen.qcm = qcm
                        modifier = True
                    else:
                        response_data["message"] = "qcm non trouver"

                if "duree" in form:
                    duree = form.get("duree")
                    examen.duree = duree
                    modifier = True

                if "point" in form:
                    point = form.get("point")
                    examen.point = point
                    modifier = True

                if modifier:
                    examen.save()
                    response_data["etat"] = True
                    response_data["message"] = "success"

            else:
                response_data["message"] = "examen non trouver"

    return HttpResponse(json.dumps(response_data), content_type="application/json")


@csrf_exempt
def examen_del(request):
    response_data = {'message': "requette invalide", 'etat': False}

    if request.method == "POST":
        form = dict()
        try:
            form = json.loads(request.body.decode("utf-8"))
        except:
            ...

        if "id" in form:
            id = form.get("id")

            examen = Examen.objects.all().filter(id=id).first()
            if examen:
                examen.delete()
                response_data["etat"] = True
                response_data["message"] = "success"
            else:
                response_data["message"] = "examen non trouver"

    return HttpResponse(json.dumps(response_data), content_type="application/json")


@csrf_exempt
def examen_get_un(request, id):
    response_data = {'message': "requette invalide", 'etat': False}

    examen = Examen.objects.all().filter(id=id).first()

    if examen:
        data = {
            "nom": examen.nom,
            "duree": examen.duree,
            "point": examen.point,
            "apprenant_id": examen.apprenant.id,
            "qcm_id": examen.qcm.id,
            "date": str(examen.date),
        }

        response_data["etat"] = True
        response_data["message"] = "success"
        response_data["donnee"] = data
    else:
        response_data["message"] = "examen non trouver"

    return HttpResponse(json.dumps(response_data), content_type="application/json")


@csrf_exempt
def examen_get_all(request):
    response_data = {'message': "requette invalide", 'etat': False}

    examen = Examen.objects.all()

    all_examen = list()

    for ex in examen:
        all_examen.append(
            {
                "nom": ex.nom,
                "duree": ex.duree,
                "point": ex.point,
                "apprenant_id": ex.apprenant.id,
                "qcm_id": ex.qcm.id,

            }
        )

    if len(all_examen) > 0:
        response_data["etat"] = True
        response_data["message"] = "success"
        response_data["donnee"] = all_examen
    else:
        response_data["message"] = "vide"

    return HttpResponse(json.dumps(response_data), content_type="application/json")


@csrf_exempt
def examen_get(request):
    response_data = {'message': "Requête invalide", 'etat': False}

    if request.method == "POST":
        try:
            form = json.loads(request.body.decode("utf-8"))
        except json.JSONDecodeError:
            return JsonResponse({'message': "Erreur lors de la lecture des données JSON", 'etat': False})

        all_examen = Examen.objects.all()
        filtrer = False

        apprenant_id = form.get("apprenant_id")
        if apprenant_id:
            apprenant = Utilisateur.objects.filter(id=apprenant_id).first()
            if apprenant:
                all_examen = all_examen.filter(apprenant=apprenant)
                filtrer = True
            else:
                return JsonResponse({'message': "Apprenant non trouvé", 'etat': False})

        qcm_id = form.get("qcm_id")
        if qcm_id:
            qcm = Qcm.objects.filter(id=qcm_id).first()
            if qcm:
                all_examen = all_examen.filter(qcm=qcm)
                filtrer = True
            else:
                return JsonResponse({'message': "QCM non trouvé", 'etat': False})

        if filtrer:
            data = []
            for ex in all_examen:
                data.append({
                    "nom": ex.nom,
                    "duree": ex.duree,
                    "point": ex.point,
                    "apprenant_id": ex.apprenant.id,
                    "qcm_id": ex.qcm.id,
                    "date": str(ex.date)
                })

            if data:
                response_data["etat"] = True
                response_data["message"] = "Success"
                response_data["donnee"] = data
            else:
                response_data["message"] = "Aucun examen trouvé"

    return JsonResponse(response_data)


@csrf_exempt
def examen_resultat_add(request):
    response_data = {'message': "requette invalide", 'etat': False}

    if request.method == "POST":
        form = dict()
        try:
            form = json.loads(request.body.decode("utf-8"))
        except:
            ...

        if "examen_id" in form and "question_id" in form and "response_id" in form:
            examen_id = form.get("examen_id")
            question_id = form.get("question_id")
            response_id = form.get("response_id")

            examen = Examen.objects.all().filter(id=examen_id).first()

            if examen:
                question = Question.objects.all().filter(id=question_id).first()

                if question:

                    response = Reponse.objects.all().filter(id=response_id).first()
                    if response:
                        new_resultat_examen = ResultatExamen(examen=examen, question=question, response=response)
                        new_resultat_examen.save()
                        response_data["message"] = "success"
                        response_data["etat"] = True
                        response_data["id"] = new_resultat_examen.id
                    else:
                        response_data["message"] = "response non trouver"
                else:
                    response_data["message"] = "question non trouver"
            else:
                response_data["message"] = "examen non trouver"

    return HttpResponse(json.dumps(response_data), content_type="application/json")


@csrf_exempt
def examen_resultat_get(request):
    response_data = {'message': "requette invalide", 'etat': False}

    if request.method == "POST":
        form = dict()
        try:
            form = json.loads(request.body.decode("utf-8"))
        except:
            ...

        if "examen_id" in form:
            examen_id = form.get("examen_id")

            examen = Examen.objects.all().filter(id=examen_id).first()

            if examen:
                resultat = ResultatExamen.objects.all().filter(examen=examen)

                all_resultat = list()

                for res in resultat:
                    all_resultat.append(
                        {
                            "examen_id": res.examen_id,
                            "question_id": res.question.id,
                            "question_question": res.question.question,
                            "response_id": res.response.id,
                            "response_reponse": res.response.reponse,
                            "response_correcte": res.response.correcte,
                        }
                    )

                if len(all_resultat):
                    response_data["etat"] = True
                    response_data["message"] = "success"
                    response_data["donnee"] = all_resultat
                else:
                    response_data["message"] = "vide"
            else:
                response_data["message"] = "examen non trouver"

    return HttpResponse(json.dumps(response_data), content_type="application/json")


@csrf_exempt
def examen_resultat_get_un(request, id):
    response_data = {'message': "requette invalide", 'etat': False}

    resultat = ResultatExamen.objects.all().filter(id=id)

    if resultat:
        resultat_data = {
            "examen_id": resultat.examen_id,
            "question_id": resultat.question.id,
            "question_question": resultat.question.question,
            "response_id": resultat.response.id,
            "response_reponse": resultat.response.reponse,
            "response_correcte": resultat.response.correcte,
        }

        response_data["etat"] = True
        response_data["message"] = "success"
        response_data["donnee"] = resultat_data
    else:
        response_data["message"] = "resultat de d'examen non trouver"

    return HttpResponse(json.dumps(response_data), content_type="application/json")


@csrf_exempt
def examen_resultat_all(request):
    response_data = {'message': "requette invalide", 'etat': False}

    if request.method == "POST":
        form = dict()
        try:
            form = json.loads(request.body.decode("utf-8"))
        except:
            ...

        resultat = ResultatExamen.objects.all()
        all_resultat = list()

        for res in resultat:
            all_resultat.append(
                {
                    "examen_id": res.examen_id,
                    "question_id": res.question.id,
                    "question_question": res.question.question,
                    "response_id": res.response.id,
                    "response_reponse": res.response.reponse,
                    "response_correcte": res.response.correcte,
                }
            )

        if len(all_resultat):
            response_data["etat"] = True
            response_data["message"] = "success"
            response_data["donnee"] = all_resultat
        else:
            response_data["message"] = "vide"

    return HttpResponse(json.dumps(response_data), content_type="application/json")


@csrf_exempt
def examen_resultat_del(request):
    response_data = {'message': "requette invalide", 'etat': False}

    if request.method == "POST":
        form = dict()
        try:
            form = json.loads(request.body.decode("utf-8"))
        except:
            ...

        if "id" in form:
            id = form.get("id")

            exame_result = ResultatExamen.objects.all().filter(id=id).first()

            if exame_result:
                exame_result.delete()
            else:
                response_data["message"] = "resultat de l'examen"

    return HttpResponse(json.dumps(response_data), content_type="application/json")


@csrf_exempt
def ordre_paiement(request):
    response_data = {'message': "requette invalide", 'etat': False}

    if request.method == "POST":
        form = dict()
        try:
            form = json.loads(request.body.decode("utf-8"))
        except:
            ...

        if "moyen_paiement" in form and "formation_id" in form and "client_id":

            moyen_paiement = form.get("moyen_paiement")
            formation_id = form.get("formation_id")
            client_id = form.get("client_id")

            formation = Formation.objects.all().filter(id=formation_id).first()
            if formation:
                client = Utilisateur.objects.all().filter(id=client_id).first()

                if client:

                    ordre_donner = False
                    order_id = get_order_id(formation_order_id_len)

                    while PaiementFormation.objects.all().filter(order_id=order_id).first():
                        order_id = get_order_id(formation_order_id_len)

                    montant = form.get("montant") if "montant" in form else formation.prix

                    strip_link = None
                    description = form.get("description")

                    tm = reverse('paiement_formation_callback', kwargs={'order_id': "seyba"})
                    notify_url = f"{request.scheme}://{request.get_host()}{tm}"

                    operation = None

                    # TODO verifier si le montant est supperieur à un minimum ?

                    numero = form.get("numero")

                    if moyen_paiement == "Orange Money":
                        # paiement orange
                        if numero and verifier_numero(numero):
                            operation = paiement_orange(
                                montant=montant,
                                numero=numero,
                                order_id=order_id,
                                notify_url=notify_url
                            )

                            if operation:
                                if operation["etat"] == "OK":
                                    ordre_donner = True
                                    response_data["etat"] = True
                                    response_data["message"] = operation["message"]
                            else:
                                response_data["message"] = response_data["message"] = operation["message"]
                        else:
                            response_data["message"] = "numero invalide"


                    elif moyen_paiement == "Moov Money":

                        if numero and verifier_numero(numero):
                            operation = paiement_moov(montant=montant,
                                                      numero=numero,
                                                      order_id=order_id,
                                                      description=f"{description}",
                                                      remarks="remarks",
                                                      notify_url=notify_url)

                            if operation and operation["status"] == 0 and operation["etat"] == "OK":
                                ordre_donner = True
                                response_data["etat"] = True
                                response_data["message"] = operation["message"]
                            else:
                                response_data["message"] = "Une erreur s'est produite"
                                try:
                                    if "message" in operation:
                                        response_data["message"] = operation["message"]
                                except:
                                    ...

                        else:
                            response_data["message"] = "numero invalide"

                    elif moyen_paiement == "Sama Money":

                        if numero and verifier_numero(numero):
                            operation = sama_pay(montant=montant,
                                                 order_id=order_id,
                                                 numero=numero,
                                                 description=f"{description}",
                                                 notify_url=notify_url)
                            if operation and operation["etat"] == "OK" and operation["status"] == 1:
                                ordre_donner = True
                                response_data["etat"] = True
                                response_data["message"] = operation["msg"]
                            else:
                                response_data["message"] = operation["message"]
                        else:
                            response_data["message"] = "numero invalide"


                    elif moyen_paiement == "Carte Visa":
                        if "return_url" in form and "name" in form:
                            return_url = form.get("return_url")
                            name = form.get("name")

                            description = f"{description}"

                            name = f"{name}"  # TODO

                            operation = stripe_pay(montant=montant,
                                                   name=name,
                                                   description=description,
                                                   return_url=return_url,
                                                   order_id=order_id,
                                                   notify_url=notify_url)

                            if operation and operation["etat"] == "OK":
                                response_data["url"] = operation["url"]
                                strip_link = operation["url"]
                                ordre_donner = True
                            else:
                                response_data["message"] = operation["message"]


                    else:
                        response_data["message"] = "moyen de paiement invalide"

                    if not ordre_donner:
                        # verification
                        operation = verifier_status(order_id)

                        if "message" in operation and "operator" in operation:
                            ordre_donner = True

                    if ordre_donner:
                        new_paiement = PaiementFormation(order_id=order_id,
                                                         moyen_paiement=moyen_paiement,
                                                         montant=montant,
                                                         formation=formation,
                                                         client=client,
                                                         numero=numero)

                        if strip_link:
                            new_paiement.strip_link = strip_link

                        new_paiement.save()

                        response_data["message"] = "Paiement enregistré, en attente de confirmation du client"
                        response_data["etat"] = True
                        response_data["order_id"] = order_id
                    else:
                        ...
                        # response_data["message"] = "une erreur s'est produit."

                else:
                    response_data["message"] = "utilisateur non trouver"
            else:
                response_data["message"] = "formation non trouver"

    return HttpResponse(json.dumps(response_data), content_type="application/json")


@csrf_exempt
def pay_formation_get_historique(request):
    response_data = {'message': "requette invalide", 'etat': False}

    if request.method == "POST":
        form = dict()
        try:
            form = json.loads(request.body.decode("utf-8"))
        except:
            ...

        filtrer = False
        historique = PaiementFormation.objects.all()
        if "formation_id" in form:
            formation_id = form.get("formation_id")

            formation = Formation.objects.all().filter(id=formation_id).first()

            if formation:
                historique = historique.filter(formation=formation)
                filtrer = True

            else:
                response_data["message"] = "vide"

        if "utilisateur_id" in form:
            utilisateur_id = form.get("utilisateur_id")

            client = Utilisateur.objects.all().filter(id=utilisateur_id).first()

            if client:
                historique = historique.filter(client=client)
                filtrer = True
            else:
                response_data["message"] = "utilisateur non trouver"

        if "all" in form:
            filtrer = True

        historique_data = list()

        for h in historique:
            historique_data.append(
                {
                    "order_id": h.order_id,
                    "payer": h.payer,
                    "moyen_paiement": h.moyen_paiement,
                    "date_soumission": str(h.date_soumission),
                    "date_validation": str(h.date_validation),
                    "montant": h.montant,
                    "formation": {
                        "slug": h.formation.slug,
                        "id": h.formation.id,
                        "nom": h.formation.nom,
                    },
                    "client_id": h.client.id,
                    "numero": h.numero,
                    "strip_link": h.strip_link,
                }
            )
        if len(historique_data) > 0:
            response_data["etat"] = True
            response_data["message"] = "success"
            response_data["donnee"] = historique_data
        else:
            response_data["message"] = "vide"

    return HttpResponse(json.dumps(response_data), content_type="application/json")


@csrf_exempt
def pay_formation_verifier(request):
    response_data = {'message': "requette invalide", 'etat': False}

    if request.method == "POST":
        form = dict()
        try:
            form = json.loads(request.body.decode("utf-8"))
        except:
            ...

        if "order_id" in form:
            order_id = form.get("order_id")

            paiement_formation = PaiementFormation.objects.all().filter(order_id=order_id).first()

            if paiement_formation:
                operation = verifier_status(order_id)

                if not paiement_formation.payer:
                    if operation and operation["etat"] == "OK":
                        new_cour = Cour(apprenant=paiement_formation.client,
                                        formation=paiement_formation.formation,
                                        montant=paiement_formation.montant)
                        new_cour.save()

                        paiement_formation.payer = True
                        paiement_formation.date_validation = str(datetime.datetime.now())

                        paiement_formation.save()

                        response_data["etat"] = True
                        response_data["message"] = "success"
                        response_data["id"] = new_cour.id

                    else:
                        response_data["message"] = operation["message"]

                else:
                    response_data["message"] = "operation deja ternimer"

            else:
                response_data["message"] = "opertion non trouver"

    return HttpResponse(json.dumps(response_data), content_type="application/json")


@csrf_exempt
def paiement_formation_callback(request, order_id):
    response_data = {'message': "requette invalide", 'etat': False}

    if request.method == "POST":
        form = dict()
        try:
            form = json.loads(request.body.decode("utf-8"))
        except:
            ...

        paiement_formation = PaiementFormation.objects.all().filter(order_id=order_id).first()

        if paiement_formation:
            operation = verifier_status(order_id)

            if not paiement_formation.payer:
                if operation and operation["etat"] == "OK":
                    new_cour = Cour(apprenant=paiement_formation.client,
                                    formation=paiement_formation.formation,
                                    montant=paiement_formation.montant)
                    new_cour.save()

                    paiement_formation.payer = True
                    paiement_formation.date_validation = str(datetime.datetime.now())

                    paiement_formation.save()

                    response_data["etat"] = True
                    response_data["message"] = "success"
                    response_data["id"] = new_cour.id

                else:
                    response_data["message"] = operation["message"]

            else:
                response_data["message"] = "operation deje ternimer"

        else:
            response_data["message"] = "opertion non trouver"

    return HttpResponse(json.dumps(response_data), content_type="application/json")



### WEB FORMATION

def admin_formation_liste(request):

    return render(request, "formation/admin/admin_formation_liste.html")
