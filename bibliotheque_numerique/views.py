import json

from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from .models import Categorie, Auteur, Livre

from root.outil import base64_to_image

from utilisateur.models import Utilisateur

# Create your views here.

"""
Categorie
"""


@csrf_exempt
def add_categorie(request):
    response_data = {'message': "Requete invalide", 'etat': False}

    if request.method == "POST":
        try:
            form = json.loads(request.body.decode("utf-8"))
        except:
            return JsonResponse({'message': "Erreur lors de la lecture des donnees JSON", 'etat': False})

        if "nom" in form and "image" in form and "description" in form:
            nom = form.get("nom")
            description = form.get("description")
            image_data = form.get("image")
            image = base64_to_image(image_data)

            new_categorie = Categorie(nom=nom, image=image, description=description)
            new_categorie.save()

            response_data["etat"] = True
            response_data["id"] = new_categorie.id
            response_data["slug"] = new_categorie.slug
            response_data["message"] = "success"
        else:
            response_data["message"] = "Nom de catégorie ou image ou description manquant"

    return JsonResponse(response_data)


@csrf_exempt
def del_categorie(request):
    response_data = {'message': "Requête invalide", 'etat': False}

    if request.method == "POST":
        try:
            form = json.loads(request.body.decode("utf-8"))
            id = form.get("id")
            slug = form.get("slug")
        except json.JSONDecodeError:
            return JsonResponse({'message': "Erreur lors de la lecture des données JSON", 'etat': False})

        if id or slug:
            if id:
                categorie_from_database = Categorie.objects.filter(id=id).first()
            else:
                categorie_from_database = Categorie.objects.filter(slug=slug).first()

            if not categorie_from_database:
                response_data["message"] = "Catégorie non trouvée"
            else:
                categorie_from_database.delete()
                response_data["etat"] = True
                response_data["message"] = "Success"
        else:
            response_data["message"] = "ID ou slug de la catégorie manquant"

    return JsonResponse(response_data)


@csrf_exempt
def get_categorie(request):
    response_data = {'message': "Requete invalide", 'etat': False}

    if request.method == "POST":
        try:
            form = json.loads(request.body.decode("utf-8"))
        except:
            return JsonResponse({'message': "Erreur lors de le lecture des donnees JSON", 'etat': False})

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
            data = []
            for cat in all_categorie:
                data.append({
                    "id": cat.id,
                    "slug": cat.slug,
                    "nom": cat.nom,
                    "image": cat.image.url,
                    "description": cat.description,
                    "date": str(cat.date),
                    "livre": [
                        {
                            "id": live.id,
                            "slug": live.slug,
                            "nom": live.nom,
                            "auteur": live.auteur.nom,
                            "date": live.date,
                            "reference": live.reference,
                            "description": live.description,
                            "image": live.image.url if live.image else None,
                        } for live in cat.all_livre
                    ]
                })

            if data:
                response_data["etat"] = True
                response_data["message"] = "success"
                response_data["donnee"] = data
            else:
                response_data["message"] = "Aucun categorie trouver"

    return JsonResponse(response_data)


@csrf_exempt
def get_categorie_un(request, id):
    response_data = {'message': "requette invalide", 'etat': False}

    categorie = Categorie.objects.all().filter(id=id).first()

    if categorie:
        categorie_data = {
            "id": categorie.id,
            "nom": categorie.nom,
            "description": categorie.description,
            "image": categorie.image.url,
        }

        response_data["etat"] = True
        response_data["message"] = "success"
        response_data["donnee"] = categorie_data
    else:
        response_data["message"] = "categorie non trouver"

    return JsonResponse(response_data)


@csrf_exempt
def set_categorie(request):
    response_data = {'message': "Requête invalide", 'etat': False}

    if request.method == "POST":
        try:
            form = json.loads(request.body.decode("utf-8"))
        except json.JSONDecodeError:
            return JsonResponse({'message': "Erreur lors de la lecture des donnees JSON", 'etat': False})

        identifiant = form.get("id")
        slug = form.get("slug")
        if not (identifiant or slug):
            return JsonResponse({'message': "ID ou slug de la categorie manquant", 'etat': False})

        categorie_from_database = None
        if identifiant:
            categorie_from_database = Categorie.objects.filter(id=identifiant).first()
        else:
            categorie_from_database = Categorie.objects.filter(slug=slug).first()

        if not categorie_from_database:
            return JsonResponse({'message': "Catégorie non trouvée", 'etat': False})

        modifier = False
        if "nom" in form:
            categorie_from_database.nom = form["nom"]
            modifier = True

        if "description" in form:
            categorie_from_database.description = form["description"]
            modifier = True

        if "image" in form:
            image_data = form.get("image")

            image = base64_to_image(image_data)
            categorie_from_database.image = image
            modifier = True

        if modifier:
            categorie_from_database.save()
            response_data["etat"] = True
            response_data["message"] = "Success"

    return JsonResponse(response_data)


"""
Auteur
"""


@csrf_exempt
def add_auteur(request):
    response_data = {'message': "Requete invalide", 'etat': False}

    if request.method == "POST":
        try:
            form = json.loads(request.body.decode("utf-8"))
        except:
            return JsonResponse({'message': "Erreur lors de la lecture des donnees JSON", 'etat': False})

        if "nom" in form and "description" in form and "admin_id" in form:
            nom = form.get("nom")
            description = form.get("description")
            admin_id = form.get("admin_id")

            admin = Utilisateur.objects.all().filter(id=admin_id).first()

            if not admin:
                return JsonResponse({'message': "Admin non trouvee", 'etat': False})
            else:

                new_auteur = Auteur(nom=nom, admin=admin, description=description)
                new_auteur.save()

                response_data["etat"] = True
                response_data["id"] = new_auteur.id
                response_data["message"] = "success"
        else:
            response_data["message"] = "Nom de l'auteur ou description manquant"

    return JsonResponse(response_data)


@csrf_exempt
def del_auteur(request):
    response_data = {'message': "Requête invalide", 'etat': False}

    if request.method == "POST":
        try:
            form = json.loads(request.body.decode("utf-8"))
            id = form.get("id")

        except json.JSONDecodeError:
            return JsonResponse({'message': "Erreur lors de la lecture des données JSON", 'etat': False})

        if id:

            auteur_from_database = Auteur.objects.filter(id=id).first()

            if not auteur_from_database:
                response_data["message"] = "Auteur non trouver"
            else:
                auteur_from_database.delete()
                response_data["etat"] = True
                response_data["message"] = "Success"
        else:
            response_data["message"] = "ID  de l'auteur manquant"

    return JsonResponse(response_data)


@csrf_exempt
def get_auteur(request):
    response_data = {'message': "Requete invalide", 'etat': False}

    if request.method == "POST":
        try:
            form = json.loads(request.body.decode("utf-8"))
        except:
            return JsonResponse({'message': "Erreur lors de le lecture des donnees JSON", 'etat': False})

        all_auteur = Auteur.objects.all()
        filtrer = False

        auteur_id = form.get("id")
        if auteur_id:
            all_auteur = all_auteur.filter(id=auteur_id)
            filtrer = True

        auteur_slug = form.get("slug")
        if auteur_slug:
            all_auteur = all_auteur.filter(slug=auteur_slug)
            filtrer = True

        categorie_all = form.get("all")
        if categorie_all:
            all_auteur = Auteur.objects.all()
            filtrer = True

        if filtrer:
            data = []
            for au in all_auteur:
                data.append({
                    "id": au.id,
                    "slug": au.slug,
                    "nom": au.nom,
                    "description": au.description,
                    "date": str(au.date),
                })

            if data:
                response_data["etat"] = True
                response_data["message"] = "success"
                response_data["donnee"] = data
            else:
                response_data["message"] = "Aucun auteur trouver"

    return JsonResponse(response_data)



@csrf_exempt
def get_auteur_un(request, id):
    response_data = {'message': "requette invalide", 'etat': False}

    auteur = Auteur.objects.all().filter(id=id).first()

    if auteur:
        auteur_data = {
            "id": auteur.id,
            "nom": auteur.nom,
            "description": auteur.description,

        }

        response_data["etat"] = True
        response_data["message"] = "success"
        response_data["donnee"] = auteur_data
    else:
        response_data["message"] = "auteur non trouver"

    return JsonResponse(response_data)


@csrf_exempt
def set_auteur(request):
    response_data = {'message': "Requête invalide", 'etat': False}

    if request.method == "POST":
        try:
            form = json.loads(request.body.decode("utf-8"))
        except json.JSONDecodeError:
            return JsonResponse({'message': "Erreur lors de la lecture des données JSON", 'etat': False})

        identifiant = form.get("id")

        if not identifiant:
            return JsonResponse({'message': "ID de l'auteur manquant", 'etat': False})

        auteur_from_database = None
        if identifiant:
            auteur_from_database = Auteur.objects.filter(id=identifiant).first()

        if not auteur_from_database:
            return JsonResponse({'message': "Auteur non trouver", 'etat': False})

        modifier = False
        if "nom" in form:
            auteur_from_database.nom = form["nom"]
            modifier = True

        if "description" in form:
            auteur_from_database.description = form["description"]
            modifier = True

        if modifier:
            auteur_from_database.save()
            response_data["etat"] = True
            response_data["message"] = "Success"

    return JsonResponse(response_data)


"""
Livre
"""


@csrf_exempt
def add_livre(request):
    response_data = {'message': "Requete invalide", 'etat': False}

    if request.method == "POST":
        try:
            form = json.loads(request.body.decode("utf-8"))
        except:
            return JsonResponse({'message': "Erreur lors de la lecture des donnees JSON", 'etat': False})
        print(form)

        nom = form.get("nom")
        description = form.get("description")
        admin_id = form.get("admin_id")
        reference = form.get("reference")
        categorie_id = form.get("categorie_id")
        auteur_id = form.get("auteur_id")
        image_data = form.get("image")
        image = base64_to_image(image_data)
        document_data = form.get("document")
        document = base64_to_image(document_data)

        if admin_id:

            admin = Utilisateur.objects.all().filter(id=admin_id).first()

            if admin:
                auteur = Auteur.objects.all().filter(id=auteur_id).first()

                if auteur:
                    categorie = Categorie.objects.all().filter(id=categorie_id).first()

                    if categorie:

                        new_livre = Livre(nom=nom, image=image, document=document, description=description, admin=admin, auteur=auteur, categorie=categorie, reference=reference)
                        new_livre.save()

                        response_data["etat"] = True
                        response_data["id"] = new_livre.id
                        response_data["slug"] = new_livre.slug
                        response_data["message"] = "success"
                    else:
                        return JsonResponse({'message': "Categorie non trouvee", 'etat': False})
                else:
                    return JsonResponse({'message': "Auteur non trouvee", 'etat': False})
            else:
                return JsonResponse({'message': "Admin non trouvee", 'etat': False})

        else:
            response_data["message"] = "Nom de livre ou image ou description manquant"

    return JsonResponse(response_data)


@csrf_exempt
def del_livre(request):
    response_data = {'message': "Requete invalide", 'etat': False}

    if request.method == "POST":
        try:
            form = json.loads(request.body.decode("utf-8"))
            id = form.get("id")
            slug = form.get("slug")
        except json.JSONDecodeError:
            return JsonResponse({'message': "Erreur lors de la lecture des donnees JSON", 'etat': False})

        if id or slug:
            if id:
                livre_from_database = Livre.objects.filter(id=id).first()
            else:
                livre_from_database = Livre.objects.filter(slug=slug).first()

            if not livre_from_database:
                response_data["message"] = "Catégorie non trouvée"
            else:
                livre_from_database.delete()
                response_data["etat"] = True
                response_data["message"] = "Success"
        else:
            response_data["message"] = "ID ou slug de la catégorie manquant"

    return JsonResponse(response_data)


@csrf_exempt
def get_livre(request):
    response_data = {'message': "Requete invalide", 'etat': False}

    if request.method == "POST":
        try:
            form = json.loads(request.body.decode("utf-8"))
        except:
            return JsonResponse({'message': "Erreur lors de le lecture des donnees JSON", 'etat': False})

        all_livre = Livre.objects.all()
        filtrer = False

        livre_id = form.get("id")
        if livre_id:
            all_livre = all_livre.filter(id=livre_id)
            filtrer = True

        livre_slug = form.get("slug")
        if livre_slug:
            all_livre = all_livre.filter(slug=livre_slug)
            filtrer = True

        categorie_slug = form.get("categorie_slug")

        if categorie_slug:
            cate = Categorie.objects.all().filter(slug=categorie_slug).first()
            all_livre = all_livre.filter(categorie=cate)
            filtrer = True

        livre_all = form.get("all")
        if livre_all:
            all_livre = Livre.objects.all()
            filtrer = True

        if filtrer:
            # print(filtrer)
            data = []
            for liv in all_livre:
                data.append({
                    "id": liv.id,
                    "slug": liv.slug,
                    "nom": liv.nom,
                    "auteur": liv.auteur.nom,
                    "categorie": liv.categorie.nom,
                    "reference": liv.reference,
                    "description": liv.description,
                    "image": liv.image.url if liv.image else None,
                    "document": liv.document.url if liv.document else None,
                    "date": str(liv.date),
                })

            if data:
                response_data["etat"] = True
                response_data["message"] = "success"
                response_data["donnee"] = data
            else:
                response_data["message"] = "Aucun categorie trouver"

    return JsonResponse(response_data)


@csrf_exempt
def get_livre_un(request, id):
    response_data = {'message': "requette invalide", 'etat': False}

    livre = Livre.objects.all().filter(id=id).first()

    if livre:
        livre_data = {
            "id": livre.id,
            "nom": livre.nom,
            "description": livre.description,
            "reference": livre.reference,
            "image": livre.image.url,
            "document": livre.document.url,
            "auteur": livre.auteur.id,
            "categorie": livre.categorie.id,

        }

        response_data["etat"] = True
        response_data["message"] = "success"
        response_data["donnee"] = livre_data
    else:
        response_data["message"] = "livre non trouver"

    return JsonResponse(response_data)


@csrf_exempt
def set_livre(request):
    response_data = {'message': "Requete invalide", 'etat': False}

    if request.method == "POST":
        try:
            form = json.loads(request.body.decode("utf-8"))
        except json.JSONDecodeError:
            return JsonResponse({'message': "Erreur lors de la lecture des donnees JSON", 'etat': False})

        slug = form.get("slug")
        identifiant = form.get("id")
        if not (identifiant or slug):
            return JsonResponse({'message': "ID ou slug de livre manquant", 'etat': False})

        livre_from_database = None
        if identifiant:
            livre_from_database = Livre.objects.filter(id=identifiant).first()
        else:
            livre_from_database = Livre.objects.filter(slug=slug).first()

        if livre_from_database:

            modifier = False
            if "nom" in form:
                livre_from_database.nom = form["nom"]
                modifier = True

            if "description" in form:
                livre_from_database.description = form["description"]
                modifier = True

            if "reference" in form:
                livre_from_database.description = form["reference"]
                modifier = True

            if "description" in form:
                livre_from_database.description = form["description"]
                modifier = True

            if "image" in form:
                image_data = form.get("image")

                image = base64_to_image(image_data)
                livre_from_database.image = image
                modifier = True

            categorie_id = form.get("categorie_id")
            if categorie_id:

                categorie = Categorie.objects.all().filter(id=categorie_id).first()

                if categorie:
                    livre_from_database.categorie = categorie
                    modifier = True
                else:
                    response_data["message"] = "categorie non trouver"

            auteur_id = form.get("auteur_id")
            if auteur_id:

                auteur = Auteur.objects.all().filter(id=auteur_id).first()

                if auteur:
                    livre_from_database.auteur = auteur
                    modifier = True
                else:
                    response_data["message"] = "auteur non trouver"

            if modifier:
                livre_from_database.save()
                response_data["etat"] = True
                response_data["message"] = "Success"

        else:
            return JsonResponse({'message': "Livre non trouvee", 'etat': False})

    return JsonResponse(response_data)

