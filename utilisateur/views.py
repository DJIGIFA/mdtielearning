import json
import random
import string

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

from formation.models import Formation
from root.outil import base64_to_image
from .models import Utilisateur, Universite


# Create your views here.


# Pour la connexion [POST]
@csrf_exempt
def api_user_login(request):
    response_data = {'message': "requette invalide", 'etat': False}

    if request.method == "POST":
        try:
            form = json.loads(request.body.decode("utf-8"))
        except:
            form = []
        if "username" in form and "password" in form:
            username = form.get("username")
            password = form.get("password")

            user = authenticate(request, username=username, password=password)
            if user is not None:
                response_data["etat"] = True
                response_data["id"] = user.id
                response_data["message"] = "success"

            else:
                user = Utilisateur.objects.all().filter(username=username).first()
                if user is not None:
                    response_data["message"] = "mot de passe incorrest"
                else:
                    response_data["message"] = "utilisateur non trouvé"

    return HttpResponse(json.dumps(response_data), content_type="application/json")


@csrf_exempt
def api_user_register(request):
    message = "requette invalide"
    id = ""
    etat = False

    if request.method == "POST":
        try:
            form = json.loads(request.body.decode("utf-8"))
        except:
            form = []

        print(form)

        # form = json.loads(request.body.decode("utf-8"))
        if ("username" in form
                and "password" in form
                and "first_name" in form
                and "last_name" in form
                and "email" in form
                and "numero"
                and "type_compte" in form):
            username = form.get("username")
            password = form.get("password")
            first_name = form.get("first_name")
            last_name = form.get("last_name")
            email = form.get("email")
            numero = form.get("numero")
            type_compte = form.get("type_compte")

            tmp_user = Utilisateur.objects.all().filter(username=username).first()
            if tmp_user:
                message = "ce non d'utilisateur est déjà utiliser"
            else:
                tmp_user = Utilisateur.objects.all().filter(numero=numero).first()

                if tmp_user:
                    message = "ce numero est déjà utiliser"
                else:
                    tmp_user = Utilisateur.objects.all().filter(email=email).first()

                    if tmp_user:
                        message = "cet email est déjà utiliser"
                    else:
                        Utilisateur.objects.create_user(
                            first_name=first_name,
                            last_name=last_name,
                            username=username,
                            email=email,
                            password=password,
                            type_compte=type_compte,
                            numero=numero)

                        new_utilisateur = authenticate(request, username=username, password=password)
                        etat = True
                        id = new_utilisateur.id
                        message = "success"

                        # TODO send mail ici (mail de bienvenu)

    response_data = {'message': message, 'etat': etat, "id": id}
    return HttpResponse(json.dumps(response_data), content_type="application/json")


@csrf_exempt
def api_user_get_profil(request, id):
    message = "requette invalide"
    donnee = dict()
    etat = False

    user_form_data_base = Utilisateur.objects.all().filter(id=id).first()

    if user_form_data_base:
        donnee["first_name"] = user_form_data_base.first_name
        donnee["id"] = user_form_data_base.id
        donnee["last_name"] = user_form_data_base.last_name
        donnee["username"] = user_form_data_base.username
        donnee["sexe"] = user_form_data_base.sexe
        donnee["quartier"] = user_form_data_base.quartier
        donnee["travail"] = user_form_data_base.travail
        donnee["date_naissance"] = str(user_form_data_base.date_naissance)
        donnee["mail_verifier"] = user_form_data_base.mail_verifier

        if user_form_data_base.avatar:
            donnee["avatar"] = user_form_data_base.avatar.url
        else:
            donnee["avatar"] = None

        if user_form_data_base.attestation:
            donnee["attestation"] = user_form_data_base.attestation.url
        else:
            donnee["attestation"] = None

        if user_form_data_base.cv:
            donnee["cv"] = user_form_data_base.cv.url
        else:
            donnee["cv"] = None

        donnee["type_compte"] = user_form_data_base.type_compte
        donnee["numero"] = user_form_data_base.numero

        donnee["email"] = user_form_data_base.email

        etat = True
        message = "success"
    else:
        message = "utilisateur non trouvé"

    response_data = {'message': message, 'etat': etat, "donnee": donnee}
    return HttpResponse(json.dumps(response_data), content_type="application/json")


@csrf_exempt
def api_user_set_profil(request):
    context = {"message": "requette invalide", "etat": False}

    if request.method == "POST":
        form = list()
        try:
            form = json.loads(request.body.decode("utf-8"))
        except:
            ...

        print(form)
        if "utilisateur_id" in form:

            id = form.get("utilisateur_id")

            user_from_data_base = Utilisateur.objects.all().filter(id=id).first()

            modifier = False
            if user_from_data_base:
                if "first_name" in form:
                    first_name = form.get("first_name")
                    user_from_data_base.first_name = first_name
                    modifier = True

                    # user_from_data_base.save()

                if "last_name" in form:
                    last_name = form.get("last_name")
                    user_from_data_base.last_name = last_name
                    modifier = True

                if "quartier" in form:
                    quartier = form.get("quartier")
                    user_from_data_base.quartier = quartier
                    modifier = True

                if "status" in form:
                    status = form.get("status")
                    user_from_data_base.status = status
                    modifier = True

                if "type_compte" in form:
                    type_compte = form.get("type_compte")
                    user_from_data_base.type_compte = type_compte
                    modifier = True

                if "sexe" in form:
                    sexe = form.get("sexe")
                    user_from_data_base.sexe = sexe
                    modifier = True

                if "date_naissance" in form:
                    date_naissance = form.get("date_naissance")
                    user_from_data_base.date_naissance = date_naissance
                    modifier = True

                if "mail_verifier" in form:
                    user_from_data_base.mail_verifier = True
                    modifier = True

                if "travail" in form:
                    travail = form.get("travail")
                    user_from_data_base.travail = travail
                    modifier = True

                if "avatar" in form:
                    avatar_64 = form.get("avatar")

                    avatar = base64_to_image(avatar_64)

                    user_from_data_base.avatar = avatar
                    modifier = True

                if "cv" in form:
                    cv_64 = form.get("cv")

                    cv = base64_to_image(cv_64)

                    user_from_data_base.cv = cv
                    modifier = True

                if "attestation" in form:
                    attestation_64 = form.get("attestation")

                    attestation = base64_to_image(attestation_64)

                    user_from_data_base.attestation = attestation
                    modifier = True

                if "numero" in form:
                    numero = form.get("numero")

                    if user_from_data_base.numero != numero:
                        tmp_user = Utilisateur.objects.all().filter(numero=numero).first()
                        tmp_user1 = Utilisateur.objects.all().filter(username=numero).first()
                        if tmp_user or tmp_user1:
                            context["etat"] = False
                            context["message"] = "ce numéro est déjà utilisé"
                        else:
                            user_from_data_base.numero = numero
                            modifier = True
                    else:
                        context["message"] = "ce numéro est déjà utilisé"

                if "email" in form:
                    email = form.get("email")

                    if user_from_data_base.email != email:
                        tmp_user = Utilisateur.objects.all().filter(email=email).first()
                        tmp_user1 = Utilisateur.objects.all().filter(username=email).first()

                        if tmp_user or tmp_user1:
                            context["etat"] = False
                            context["message"] = "cet email est déjà utilisé"
                        else:
                            user_from_data_base.email = email
                            modifier = True
                    else:
                        context["message"] = "cet email est déjà utilisé"

                if "username" in form:
                    username = form.get("username")

                    if user_from_data_base.username != username:
                        tmp_user = Utilisateur.objects.all().filter(username=username).first()
                        tmp_user1 = Utilisateur.objects.all().filter(numero=username).first()

                        utiliser = False

                        if tmp_user or tmp_user1 or utiliser:
                            context["etat"] = False
                            context["message"] = "ce nom d'utilisateur est déjà utilisé"
                            # print(context)

                        else:
                            user_from_data_base.username = username
                            modifier = True
                    else:
                        context["message"] = "ce nom d'utilisateur est déjà utilisé"

                if "new_password" in form and "old_password" in form:
                    new_password = form.get("new_password")
                    old_password = form.get("old_password")
                    username = user_from_data_base.username

                    user = authenticate(request, username=username, password=old_password)
                    if user:
                        user_from_data_base.set_password(new_password)
                        modifier = True

                    else:
                        context["etat"] = False
                        context["message"] = "Mot de passe incorrect"

                if modifier:
                    user_from_data_base.save()
                    context["etat"] = True
                    context["message"] = "success"
                else:
                    ...
                # TODO requette invalide

            else:
                context["etat"] = False
                context["message"] = "utilisateur non trouvé"
    else:
        context["etat"] = False
        context["message"] = "requette invalide"

    return HttpResponse(json.dumps(context), content_type="application/json")


@csrf_exempt
def api_user_get(request):
    context = {"message": "requette invalide", "etat": False}

    if request.method == "POST":
        form = list()
        try:
            form = json.loads(request.body.decode("utf-8"))
        except:
            ...

        print(form)
        filter = False
        all_utilisateur = list()

        if "all" in form:
            all_utilisateur = Utilisateur.objects.all()
            filter = True

        elif "id" in form:
            id = form.get("id")
            all_utilisateur = Utilisateur.objects.all().filter(id=id)
            filter = True

        elif "type_compte" in form:
            type_compte = form.get("type_compte")
            all_utilisateur = Utilisateur.objects.all().filter(type_compte=type_compte)
            filter = True

        if filter:
            utilisateurs = list()

            for user in all_utilisateur:
                utilisateurs.append(
                    {
                        "avatar": user.avatar.url if user.avatar else None,
                        "type_compte": user.type_compte,
                        "username": user.username,
                        "user_id": user.id,
                        "first_name": user.first_name,
                        "last_name": user.last_name,
                        "status": user.status,
                        "email": user.email,
                        "numero": user.numero,
                        "sexe": user.sexe if user.sexe else None,
                        "quartier": user.quartier if user.quartier else None,
                        "travail": user.travail if user.travail else None,
                        "date_naissance": str(user.date_naissance) if user.date_naissance else None,
                    }
                )

            if len(utilisateurs) > 0:
                context['etat'] = True
                context['message'] = "success"
                context['donnee'] = utilisateurs
            else:
                context["etat"] = False
                context["message"] = "vide"

    return HttpResponse(json.dumps(context), content_type="application/json")



"""
Universiter
"""


@csrf_exempt
def add_universiter(request):
    response_data = {'message': "Requete invalide", 'etat': False}

    if request.method == "POST":
        try:
            form = json.loads(request.body.decode("utf-8"))
        except:
            return JsonResponse({'message': "Erreur lors de la lecture des donnees JSON", 'etat': False})

        if "nom" in form and "utilisateur_id" in form:
            nom = form.get("nom")
            utilisateur_id = form.get("utilisateur_id")
            image_data = form.get("image")
            # image = base64_to_image(image_data)

            admin = Utilisateur.objects.all().filter(id=utilisateur_id).first()
            if admin:
                new_universiter = Universite(nom=nom, utilisateur=admin)
                new_universiter.save()

                response_data["etat"] = True
                response_data["id"] = new_universiter.id
                response_data["slug"] = new_universiter.slug
                response_data["message"] = "success"
            else:
                response_data["message"] = "utilisateur non trouver"
        else:
            response_data["message"] = "Nom de Universiter manquant"

    return JsonResponse(response_data)


@csrf_exempt
def del_universiter(request):
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
                universiter_from_database = Universite.objects.filter(id=id).first()
            else:
                universiter_from_database = Universite.objects.filter(slug=slug).first()

            if not universiter_from_database:
                response_data["message"] = "universiter non trouvée"
            else:
                universiter_from_database.delete()
                response_data["etat"] = True
                response_data["message"] = "Success"
        else:
            response_data["message"] = "ID ou slug de la universiter manquant"

    return JsonResponse(response_data)


@csrf_exempt
def get_universiter(request):
    response_data = {'message': "Requete invalide", 'etat': False}

    if request.method == "POST":
        try:
            form = json.loads(request.body.decode("utf-8"))
        except:
            return JsonResponse({'message': "Erreur lors de le lecture des donnees JSON", 'etat': False})

        all_universiter = Universite.objects.all()
        filtrer = False

        universiter_id = form.get("id")
        if universiter_id:
            all_universiter = all_universiter.filter(id=universiter_id)
            filtrer = True

        universiter_slug = form.get("slug")
        if universiter_slug:
            all_universiter = all_universiter.filter(slug=universiter_slug)
            filtrer = True

        universiter_all = form.get("all")
        if universiter_all:
            all_universiter = Universite.objects.all()
            filtrer = True

        if filtrer:
            data = []
            for cat in all_universiter:
                data.append({
                    "id": cat.id,
                    "slug": cat.slug,
                    "nom": cat.nom,

                })
            
            if data:
                response_data["etat"] = True
                response_data["message"] = "success"
                response_data["donnee"] = data
            else:
                response_data["message"] = "Aucun universiter trouver"

    return JsonResponse(response_data)


@csrf_exempt
def get_universiter_un(request, id):
    response_data = {'message': "requette invalide", 'etat': False}

    universiter = Universite.objects.all().filter(id=id).first()

    if universiter:
        universiter_data = {
            "id": universiter.id,
            "nom": universiter.nom,

        }

        response_data["etat"] = True
        response_data["message"] = "success"
        response_data["donnee"] = universiter_data
    else:
        response_data["message"] = "categorie non trouver"

    return JsonResponse(response_data)


@csrf_exempt
def set_universiter(request):
    response_data = {'message': "Requête invalide", 'etat': False}

    if request.method == "POST":
        try:
            form = json.loads(request.body.decode("utf-8"))
        except json.JSONDecodeError:
            return JsonResponse({'message': "Erreur lors de la lecture des donnees JSON", 'etat': False})

        identifiant = form.get("id")
        slug = form.get("slug")
        if not (identifiant or slug):
            return JsonResponse({'message': "ID ou slug de la universiter manquant", 'etat': False})

        universiter_from_database = None
        if identifiant:
            universiter_from_database = Universite.objects.filter(id=identifiant).first()
        else:
            universiter_from_database = Universite.objects.filter(slug=slug).first()

        if not universiter_from_database:
            return JsonResponse({'message': "universiter non trouvée", 'etat': False})

        modifier = False
        if "nom" in form:
            universiter_from_database.nom = form["nom"]
            modifier = True

        if modifier:
            universiter_from_database.save()
            response_data["etat"] = True
            response_data["message"] = "Success"

    return JsonResponse(response_data)


"""
Web views
"""
def web_connexion(request):

    if request.user.is_authenticated:
        messages.success(request, "Vous êtes connectez")
        return redirect(reverse("index"))

    if request.method == "POST":
        form = request.POST
        email = form.get("email")
        password = form.get("password")

        tmp_user = Utilisateur.objects.filter(email=email).first()
        if tmp_user:
            username = tmp_user.username
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, "Connecté")
                return redirect(reverse("index"))
            else:
                messages.warning(request,"Mot de passe invalide")
        else:
            messages.error(request,"Utilisateur non trouver")


    return render(request, "utilisateur/connexion.html")


def web_deconnexion(request):
    logout(request)
    messages.success(request,"Vous êtes déconnectez")
    return redirect(reverse("index"))

def web_inscription(request):

    if request.method == "POST":
        form = request.POST
        first_name = form.get("first_name")
        last_name = form.get("last_name")
        type_compte = form.get("type_compte")
        numero = form.get("numero")
        email = form.get("email")
        password = form.get("password")
        confirm_password = form.get("confirm_password")

        tmp_user = Utilisateur.objects.all().filter(numero=numero).first()

        ok = True

        if password != confirm_password:
            messages.error(request, "mot de passe different")
            ok = False

        if tmp_user:
            messages.warning(request,"Numéro déjà utiliser")
            ok = False

        tmp_user = Utilisateur.objects.all().filter(email=email).first()
        if tmp_user:
            messages.warning(request,"Email déjà utiliser")
            ok = False

        # generation du username
        username = "".join([random.choice(string.ascii_letters) for _ in range(8)])
        while Utilisateur.objects.all().filter(username=username).first():
            username = username + random.choice(string.ascii_letters)

        if ok:
            Utilisateur.objects.create_user(
                first_name=first_name,
                last_name=last_name,
                username=username,
                email=email,
                password=password,
                type_compte=type_compte,
                numero=numero)

            new_utilisateur = authenticate(request, username=username, password=password)

            if new_utilisateur:
                login(request, new_utilisateur)
                messages.success(request, "Compte créer")

    return render(request, "utilisateur/web_inscription.html")



### Administration
def admin_index(request):
    # TODO securité

    nombre_formation = len(Formation.objects.all())

    nombre_apprenant = len(Utilisateur.objects.all().filter(type_compte="Apprenant"))
    nombre_instructeur = len(Utilisateur.objects.all().filter(type_compte="Instructeur"))
    nombre_admin = len(Utilisateur.objects.all().filter(type_compte="Admin"))


    context = {
        "nombre_formation": nombre_formation,
        "nombre_apprenant" : nombre_apprenant,
        "nombre_instructeur" :nombre_instructeur,
        "nombre_admin" :nombre_admin,
    }

    return render(request, "utilisateur/admin/admin_index.html", context=context)


def admin_instructeur_liste(request):


    all_utilisateurs = Utilisateur.objects.all().filter(type_compte="Instructeur")

    context = {
        "all_utilisateurs": all_utilisateurs,
        "nombre_instructeur": len(all_utilisateurs)
    }
    return render(request, "utilisateur/admin/admin_instructeur_liste.html",context=context)


def admin_apprenant_liste(request):

    all_utilisateurs = Utilisateur.objects.all().filter(type_compte="Apprenant")

    context = {
        "all_utilisateurs": all_utilisateurs,
        "nombre_apprenant": len(all_utilisateurs)
    }

    return render(request, "utilisateur/admin/admin_apprenant_liste.html",context=context)



def contact(request):

    return render(request,"utilisateur/contact.html")

