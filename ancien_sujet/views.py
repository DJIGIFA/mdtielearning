import datetime
import json
from django.urls import reverse

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from root.code_paiement import document_order_id_len, message_trouver_mais_pas_confirmer, message_trouver_et_comfirmer
from root.outil import base64_to_image, get_order_id, verifier_numero, paiement_orange, paiement_moov, sama_pay, \
    stripe_pay, verifier_status
from utilisateur.models import Utilisateur
from .models import Type, Niveau, Matiere, Pays, Document, PaiementDocument, DocumentAcheter


# Create your views here.


@csrf_exempt
def add_type_sujet(request):
    response_data = {'message': "requette invalide", 'etat': False}

    if request.method == "POST":
        form = dict()
        try:
            form = json.loads(request.body.decode("utf-8"))
        except:
            ...

        if "nom" in form:
            nom = form.get("nom")

            new_type = Type(nom=nom)
            new_type.save()

            response_data["message"] = "success"
            response_data['etat'] = True

    return HttpResponse(json.dumps(response_data), content_type="application/json")


@csrf_exempt
def get_type_sujet(request):
    response_data = {'message': "requette invalide", 'etat': False}

    if request.method == "POST":
        form = list()

        try:
            form = json.loads(request.body.decode("utf-8"))
        except:
            ...

        filter = False
        all_type = list()
        if "all" in form:
            all_type = Type.objects.all()
            filter = True
        elif "id" in form:
            id = form.get("id")
            all_type = Type.objects.all().filter(id=id)
            filter = True

        if filter:
            types = list()

            for t in all_type:
                types.append(
                    {
                        "id": t.id,
                        "nom": t.nom,
                    }
                )

            if len(types) > 0:
                response_data["etat"] = True
                response_data["message"] = "success"
                response_data["donnee"] = types
            else:
                response_data["message"] = "vide"

    return HttpResponse(json.dumps(response_data), content_type="application/json")


@csrf_exempt
def set_type_sujet(request):
    response_data = {'message': "requette invalide", 'etat': False}

    if request.method == "POST":
        form = dict()
        try:
            form = json.loads(request.body.decode("utf-8"))
        except:
            ...

        if "id" in form :
            id = form.get("id")

            if id:
                sous_categorie_from_database = Type.objects.all().filter(id=id).first()

            if not sous_categorie_from_database:
                response_data["message"] = "Type non trouve"
            else:
                modifier = False
                if "nom" in form:
                    nom = form.get("nom")

                    sous_categorie_from_database.nom = nom
                    modifier = True

                if modifier:
                    sous_categorie_from_database.save()
                    response_data["etat"] = True
                    response_data["message"] = "success"

    return HttpResponse(json.dumps(response_data), content_type="application/json")


@csrf_exempt
def get_type_sujet_un(request, id):
    response_data = {'message': "requette invalide", 'etat': False}

    type = Type.objects.all().filter(id=id).first()

    if type:
        type_data = {
            "id": type.id,
            "nom": type.nom,
        }
        response_data["etat"] = True
        response_data["message"] = "success"
        response_data["donnee"] = type_data

    else:
        response_data["message"] = "type non trouver"

    return HttpResponse(json.dumps(response_data), content_type="application/json")


@csrf_exempt
def del_type_sujet(request):
    response_data = {'message': "requette invalide", 'etat': False}

    if request.method == "POST":
        form = dict()
        try:
            form = json.loads(request.body.decode("utf-8"))
        except:
            ...

        if "id" in form:
            id = form.get("id")

            type = Type.objects.all().filter(id=id).first()

            if type:
                type.delete()
                response_data["etat"] = True
                response_data["message"] = "success"

            else:
                response_data["message"] = "type non trouver"

    return HttpResponse(json.dumps(response_data), content_type="application/json")


"""
Niveau
"""


@csrf_exempt
def add_niveau_sujet(request):
    response_data = {'message': "requette invalide", 'etat': False}

    if request.method == "POST":
        form = dict()
        try:
            form = json.loads(request.body.decode("utf-8"))
        except:
            ...

        if "nom" in form:
            nom = form.get("nom")

            new_niveau = Niveau(nom=nom)
            new_niveau.save()

            response_data["etat"] = True
            response_data["message"] = "success"
            response_data["id"] = new_niveau.id

    return HttpResponse(json.dumps(response_data), content_type="application/json")


@csrf_exempt
def get_niveau_sujet(request):
    response_data = {'message': "requette invalide", 'etat': False}

    niveau = Niveau.objects.all()

    all_niveau = list()

    for n in niveau:
        all_niveau.append(
            {
                "id": n.id,
                "nom": n.nom,
            }
        )

    if len(all_niveau) > 0:
        response_data["etat"] = True
        response_data["message"] = "success"
        response_data["donnee"] = all_niveau
    else:
        response_data["message"] = "vide"

    return HttpResponse(json.dumps(response_data), content_type="application/json")



@csrf_exempt
def set_niveau_sujet(request):
    response_data = {'message': "requette invalide", 'etat': False}

    if request.method == "POST":
        form = dict()
        try:
            form = json.loads(request.body.decode("utf-8"))
        except:
            ...

        if "id" in form :
            id = form.get("id")

            if id:
                sous_categorie_from_database = Niveau.objects.all().filter(id=id).first()

            if not sous_categorie_from_database:
                response_data["message"] = "Niveau non trouve"
            else:
                modifier = False
                if "nom" in form:
                    nom = form.get("nom")

                    sous_categorie_from_database.nom = nom
                    modifier = True

                if modifier:
                    sous_categorie_from_database.save()
                    response_data["etat"] = True
                    response_data["message"] = "success"

    return HttpResponse(json.dumps(response_data), content_type="application/json")

@csrf_exempt
def get_un_niveau_sujet(request, id):
    response_data = {'message': "requette invalide", 'etat': False}

    niveau = Niveau.objects.all().filter(id=id).first()

    if niveau:
        data_niveau = {
            "nom": niveau.nom,
            "id": niveau.id,
        }

        response_data["etat"] = True
        response_data["message"] = "success"
        response_data["donnee"] = data_niveau
    else:
        response_data["message"] = "niveau non trouver"

    return HttpResponse(json.dumps(response_data), content_type="application/json")


@csrf_exempt
def del_niveau_sujet(request):
    response_data = {'message': "requette invalide", 'etat': False}

    if request.method == "POST":
        form = dict()
        try:
            form = json.loads(request.body.decode("utf-8"))
        except:
            ...

        if "id" in form:
            id = form.get("id")

            niveau = Niveau.objects.all().filter(id=id).first()

            if niveau:
                niveau.delete()
                response_data["etat"] = True
                response_data["message"] = "success"
            else:
                response_data["message"] = "niveau non trouver"

    return HttpResponse(json.dumps(response_data), content_type="application/json")


"""
Matiere
"""


@csrf_exempt
def add_matiere_sujet(request):
    response_data = {'message': "requette invalide", 'etat': False}

    if request.method == "POST":
        form = dict()
        try:
            form = json.loads(request.body.decode("utf-8"))
        except:
            ...

        if "nom" in form:
            nom = form.get("nom")

            new_matiere = Matiere(nom=nom)

            new_matiere.save()
            response_data["etat"] = True
            response_data["id"] = new_matiere.id
            response_data["message"] = "success"

    return HttpResponse(json.dumps(response_data), content_type="application/json")


@csrf_exempt
def get_matiere_sujet(request):
    response_data = {'message': "requette invalide", 'etat': False}

    matiere = Matiere.objects.all()

    all_matiere = list()
    for m in matiere:
        all_matiere.append(
            {
                "id": m.id,
                "nom": m.nom,
            }
        )

    if len(all_matiere) > 0:
        response_data["etat"] = True
        response_data["message"] = "success"
        response_data["donnee"] = all_matiere
    else:
        response_data["message"] = "vide"

    return HttpResponse(json.dumps(response_data), content_type="application/json")



@csrf_exempt
def set_matiere_sujet(request):
    response_data = {'message': "requette invalide", 'etat': False}

    if request.method == "POST":
        form = dict()
        try:
            form = json.loads(request.body.decode("utf-8"))
        except:
            ...

        if "id" in form :
            id = form.get("id")

            if id:
                sous_categorie_from_database = Matiere.objects.all().filter(id=id).first()

            if not sous_categorie_from_database:
                response_data["message"] = "Matiere non trouve"
            else:
                modifier = False
                if "nom" in form:
                    nom = form.get("nom")

                    sous_categorie_from_database.nom = nom
                    modifier = True

                if modifier:
                    sous_categorie_from_database.save()
                    response_data["etat"] = True
                    response_data["message"] = "success"

    return HttpResponse(json.dumps(response_data), content_type="application/json")


@csrf_exempt
def get_matiere_sujet_un(request, id):
    response_data = {'message': "requette invalide", 'etat': False}

    matiere = Matiere.objects.all().filter(id=id).first()

    if matiere:
        response_data["etat"] = True
        response_data["message"] = "success"
        response_data["donnee"] = {
            "id": matiere.id,
            "nom": matiere.nom,
        }
    else:
        response_data["message"] = "matiere non trouver"

    return HttpResponse(json.dumps(response_data), content_type="application/json")


@csrf_exempt
def del_matiere_sujet(request):
    response_data = {'message': "requette invalide", 'etat': False}

    if request.method == "POST":
        form = dict()
        try:
            form = json.loads(request.body.decode("utf-8"))
        except:
            ...

        if "id" in form:
            id = form.get("id")

            matiere = Matiere.objects.all().filter(id=id).first()

            if matiere:
                matiere.delete()
                response_data["etat"] = True
                response_data["message"] = "success"

            else:
                response_data["message"] = "matiere non trouver"

    return HttpResponse(json.dumps(response_data), content_type="application/json")


# Pays
@csrf_exempt
def add_pays_sujet(request):
    response_data = {'message': "requette invalide", 'etat': False}

    if request.method == "POST":
        form = dict()
        try:
            form = json.loads(request.body.decode("utf-8"))
        except:
            ...

        if "nom" in form:
            nom = form.get("nom")

            new_pays = Pays(nom=nom)
            new_pays.save()
            response_data["etat"] = True
            response_data["message"] = "success"
            response_data["id"] = new_pays.id

    return HttpResponse(json.dumps(response_data), content_type="application/json")


@csrf_exempt
def del_pays_sujet(request):
    response_data = {'message': "requette invalide", 'etat': False}

    if request.method == "POST":
        form = dict()
        try:
            form = json.loads(request.body.decode("utf-8"))
        except:
            ...

        if "id" in form:
            id = form.get("id")

            pays = Pays.objects.all().filter(id=id).first()

            if pays:
                pays.delete()
                response_data["message"] = "success"
                response_data["etat"] = True
            else:
                response_data["message"] = "pays non trouver"

    return HttpResponse(json.dumps(response_data), content_type="application/json")


@csrf_exempt
def get_pays_sujet(request):
    response_data = {'message': "requette invalide", 'etat': False}

    if request.method == "POST":
        form = dict()
        try:
            form = json.loads(request.body.decode("utf-8"))
        except:
            ...

        all_pays = Pays.objects.all()

        pays = list()

        for p in all_pays:
            pays.append(
                {
                    "nom": p.nom,
                    "id": p.id
                }
            )

        if len(pays) > 0:
            response_data["etat"] = True
            response_data["message"] = "success"
            response_data["donnee"] = pays
        else:
            response_data["message"] = "vide"

    return HttpResponse(json.dumps(response_data), content_type="application/json")


@csrf_exempt
def get_pays_sujet_un(request, id):
    response_data = {'message': "requette invalide", 'etat': False}

    pays = Pays.objects.all().filter(id=id).first()

    if pays:
        pays_data = {
            "nom": pays.nom,
            "id": pays.id
        }

        response_data["etat"] = True
        response_data["message"] = "success"
        response_data["donnee"] = pays_data
    else:
        response_data["message"] = "pays non trouver"

    return HttpResponse(json.dumps(response_data), content_type="application/json")


# document
@csrf_exempt
def add_document(request):
    response_data = {'message': "requette invalide", 'etat': False}

    if request.method == "POST":
        form = dict()
        try:
            form = json.loads(request.body.decode("utf-8"))
        except:
            ...

        if ("type_id" in form
                and "niveau_id" in form
                and "pays_id" in form
                and "matiere_id" in form
                and "nom" in form
                and "document" in form
                and "prix" in form
                and "miniature" in form
                and "annee" in form):

            type_id = form.get("type_id")
            niveau_id = form.get("niveau_id")
            pays_id = form.get("pays_id")
            matiere_id = form.get("matiere_id")

            document_base_64 = form.get("document")
            miniature_base_64 = form.get("miniature")

            nom = form.get("nom")
            prix = form.get("prix")
            annee = form.get("annee")

            # type
            type = Type.objects.all().filter(id=type_id).first()

            if type:
                niveau = Niveau.objects.all().filter(id=niveau_id).first()

                # niveau
                if niveau:
                    pays = Pays.objects.all().filter(id=pays_id).first()

                    # pays
                    if pays:

                        matiere = Matiere.objects.all().filter(id=matiere_id).first()

                        if matiere:
                            document = base64_to_image(document_base_64)
                            miniature = base64_to_image(miniature_base_64)

                            new_dovument = Document(type=type,
                                                    niveau=niveau,
                                                    pays=pays,
                                                    matiere=matiere,
                                                    nom=nom,
                                                    annee=annee,
                                                    document=document,
                                                    prix=prix,
                                                    miniature=miniature)

                            new_dovument.save()

                            response_data["etat"] = True
                            response_data["message"] = "success"
                            response_data["id"] = new_dovument.id
                        else:
                            response_data["message"] = 'matiere non trouver'

                    else:
                        response_data["message"] = "pays non trouver"
                else:
                    response_data["message"] = "niveau non trouver"
            else:
                response_data["message"] = "type de sujet non trouver"

    return HttpResponse(json.dumps(response_data), content_type="application/json")


@csrf_exempt
def set_document(request):
    response_data = {'message': "requette invalide", 'etat': False}

    if request.method == "POST":
        form = dict()
        try:
            form = json.loads(request.body.decode("utf-8"))
        except:
            ...
        print(form)

        if "id" in form:
            id = form.get("id")
            document = Document.objects.all().filter(id=id).first()

            if document:
                modifier = False

                if "type_id" in form:
                    type_id = form.get("type_id")

                    type = Type.objects.all().filter(id=type_id).first()

                    if type:
                        document.type = type
                        modifier = True
                    else:
                        response_data["message"] = "type non trouver"

                if "niveau_id" in form:
                    niveau_id = form.get("niveau_id")
                    niveau = Niveau.objects.all().filter(id=niveau_id).first()

                    if niveau:
                        document.niveau = niveau
                        modifier = True
                    else:
                        response_data["message"] = "niveau non trouver"

                if "pays_id" in form:
                    pays_id = form.get("pays_id")

                    pays = Pays.objects.all().filter(id=pays_id).first()
                    if pays:
                        document.pays = pays
                        modifier = True
                    else:
                        response_data["message"] = "pays non trouver"

                if "matiere_id" in form:
                    matiere_id = form.get("matiere_id")
                    matiere = Matiere.objects.all().filter(id=matiere_id).first()

                    if matiere:
                        document.matiere = matiere
                        modifier = True
                    else:
                        response_data["message"] = "matiere non trouver"

                if "nom" in form:
                    nom = form.get("nom")
                    document.nom = nom
                    modifier = True

                if "annee" in form:
                    annee = form.get("annee")

                    document.annee = annee
                    modifier = True

                if "document" in form:
                    document_64 = form.get("document")
                    document = base64_to_image(document_64)

                    document.document = document

                    modifier = True

                if "prix" in form:
                    prix = form.get("prix")

                    document.prix = prix
                    modifier = True

                if "miniature" in form:
                    miniature_64 = form.get - ("miniature")

                    miniature = base64_to_image(miniature_64)

                    document.miniature = miniature
                    modifier = True

                if modifier:
                    document.save()
                    response_data["etat"] = True
                    response_data["message"] = "success"


            else:
                response_data["message"] = "document non trouver"
        else:
            ...  # request invalide

    return HttpResponse(json.dumps(response_data), content_type="application/json")


@csrf_exempt
def get_document_all(request):
    response_data = {'message': "requette invalide", 'etat': False}

    if request.method == "POST":
        form = dict()
        try:
            form = json.loads(request.body.decode("utf-8"))
        except:
            ...
        all_document = Document.objects.all()

        doc_liste = list()

        for d in all_document:
            doc_liste.append(
                {

                    "type_id": d.type.id,
                    "niveau_id": d.niveau.id,
                    "pays": d.pays.nom,
                    "matiere_id": d.matiere.id,
                    "nom": d.nom,
                    "id": d.id,
                    "annee": d.annee,

                    "document": d.document.url if d.document else None,
                    "miniature": d.miniature.url if d.miniature else None,
                    "prix": d.prix,
                    "date": str(d.date),
                }
            )

        if len(doc_liste) > 0:
            response_data["etat"] = True
            response_data["message"] = "success"
            response_data["donnee"] = doc_liste
        else:
            response_data["message"] = "vide"

    return HttpResponse(json.dumps(response_data), content_type="application/json")


@csrf_exempt
def get_document_un(request, id):
    response_data = {'message': "requette invalide", 'etat': False}

    document = Document.objects.all().filter(id=id).first()

    if document:
        doc_data = {
            "type": document.type.nom,
            "niveau": document.niveau.nom,
            "pays": document.pays.nom,
            "matiere": document.matiere.nom,
            "nom": document.nom,
            "annee": document.annee,

            "document": document.document.url if document.document else None,
            "miniature": document.miniature.url if document.miniature else None,
            "prix": document.prix,
            "date": str(document.date),
        }

        response_data["etat"] = True
        response_data["message"] = "success"
        response_data["donnee"] = doc_data
    else:
        response_data["message"] = "document non trouver"

    return HttpResponse(json.dumps(response_data), content_type="application/json")


@csrf_exempt
def get_document_params(request):
    response_data = {'message': "requette invalide", 'etat': False}

    if request.method == "POST":
        form = dict()
        try:
            form = json.loads(request.body.decode("utf-8"))
        except:
            ...
        all_document = Document.objects.all()

        doc_liste = list()
        filtrer = False

        if "type_id" in form:
            type_id = form.get("type_id")
            type = Type.objects.all().filter(id=type_id).first()

            if type:
                all_document = all_document.filter(type=type)
                filtrer = True
            else:
                response_data["message"] = "type non trouver"

        if "niveau_id" in form:
            niveau_id = form.get("niveau_id")

            niveau = Niveau.objects.all().filter(id=niveau_id).first()
            if niveau:
                all_document = all_document.filter(niveau=niveau)
                filtrer = True
            else:
                response_data["message"] = "niveau non trouver"

        if "pays_id" in form:
            pays_id = form.get("pays")
            pays = Pays.objects.all().filter(id=pays_id).first()

            if pays:
                all_document = all_document.filter(pays=pays)
                filtrer = True
            else:
                response_data["message"] = "pays non trouver"

        if "matiere_id" in form:
            matiere_id = form.get("matiere_id")

            matiere = Matiere.objects.all().filter(id=matiere_id).first()

            if matiere:
                all_document = all_document.filter(matiere=matiere)
                filtrer = True
            else:
                response_data["message"] = "matiere non trouver"

        if "annee" in form:
            annee = form.get("annee")

            all_document = all_document.all().filter(annee=annee)
            filtrer = True

        if filtrer:
            for d in all_document:
                doc_liste.append(
                    {
                        "id": d.id,
                        "type": d.type.nom,
                        "niveau": d.niveau.nom,
                        "pays": d.pays.nom,
                        "matiere": d.matiere.nom,
                        "nom": d.nom,
                        "annee": d.annee,

                        "document": d.document.url if d.document else None,
                        "miniature": d.miniature.url if d.miniature else None,
                        "prix": d.prix,
                        "date": str(d.date),
                    }
                )

            if len(doc_liste) > 0:
                response_data["etat"] = True
                response_data["message"] = "success"
                response_data["donnee"] = doc_liste
            else:
                response_data["message"] = "vide"

    return HttpResponse(json.dumps(response_data), content_type="application/json")


@csrf_exempt
def del_document(request):
    response_data = {'message': "requette invalide", 'etat': False}

    if request.method == "POST":
        form = dict()
        try:
            form = json.loads(request.body.decode("utf-8"))
        except:
            ...
        if "id" in form:
            id = form.get("id")

            document = Document.objects.all().filter(id=id).first()

            if document:
                document.delete()
                response_data["etat"] = True
                response_data["message"] = "success"
            else:
                response_data["message"] = "document non trouver"

    return HttpResponse(json.dumps(response_data), content_type="application/json")


# Paiment


@csrf_exempt
def ordre_paiement_document(request):
    response_data = {'message': "requette invalide", 'etat': False}

    if request.method == "POST":
        form = dict()
        try:
            form = json.loads(request.body.decode("utf-8"))
        except:
            ...

        if "moyen_paiement" in form and "document_id" in form and "client_id":

            moyen_paiement = form.get("moyen_paiement")
            document_id = form.get("document_id")
            client_id = form.get("client_id")

            document = Document.objects.all().filter(id=document_id).first()
            if document:
                client = Utilisateur.objects.all().filter(id=client_id).first()

                if client:

                    ordre_donner = False
                    order_id = get_order_id(document_order_id_len)

                    while PaiementDocument.objects.all().filter(order_id=order_id).first():
                        order_id = get_order_id(document_order_id_len)

                    montant = form.get("montant") if "montant" in form else document.prix

                    strip_link = None
                    description = form.get("description")

                    tm = reverse('paiement_document_callback', kwargs={'order_id': "seyba"})
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
                                response_data["message"] = operation["message"]

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

                            name = f"{name}"

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
                        new_paiement = PaiementDocument(order_id=order_id,
                                                        moyen_paiement=moyen_paiement,
                                                        montant=montant,
                                                        document=document,
                                                        client=client,
                                                        numero=numero)

                        if strip_link:
                            new_paiement.strip_link = strip_link
                        # response_data["message"] = "Paiement enregistré, en attente de confirmation du client"
                        response_data["etat"] = True
                        response_data["order_id"] = order_id
                    else:
                        response_data["message"] = "une erreur s'est produit."

                else:
                    response_data["message"] = "utilisateur non trouver"
            else:
                response_data["message"] = "document non trouver"

    return HttpResponse(json.dumps(response_data), content_type="application/json")


@csrf_exempt
def pay_document_get_historique(request):
    response_data = {'message': "requette invalide", 'etat': False}

    if request.method == "POST":
        form = dict()
        try:
            form = json.loads(request.body.decode("utf-8"))
        except:
            ...

        all_historique = PaiementDocument.objects.all()
        filtrer = False

        if "utilisateur_id" in form:
            utilisateur_id = form.get("utilisateur_id")

            utilisateur = Utilisateur.objects.all().filter(id=utilisateur_id).first()

            if utilisateur:
                all_historique = all_historique.filter(client=utilisateur)
                filtrer = True
            else:
                response_data["message"] = "utilisateur non trouver"

        if "document_id" in form:
            document_id = form.get("document_id")

            document = Document.objects.all().filter(id=document_id).first()

            if document:
                all_historique = all_historique.filter(document=document)
                filtrer = True
            else:
                response_data["message"] = "document non trouver"

        if "all" in form:
            filtrer = True

        if filtrer:
            liste_historique = list()

            for h in all_historique:
                liste_historique.append(
                    {
                        "order_id": h.order_id,
                        "payer": h.payer,
                        "moyen_paiement": h.moyen_paiement,
                        # "date_soumission": h.date_soumission,
                        # "date_validation": h.date_validation,
                        "montant": h.montant,
                        "document": h.document.id,
                        "client_id": h.client.id,
                        "numero": h.numero,
                        "strip_link": h.strip_link,
                    }
                )

            if len(liste_historique) > 0:
                response_data["etat"] = True
                response_data["message"] = "success"
                response_data["donnee"] = liste_historique
            else:
                response_data["message"] = "vide"

    return HttpResponse(json.dumps(response_data), content_type="application/json")


@csrf_exempt
def pay_document_verifier(request):
    response_data = {'message': "requette invalide", 'etat': False}

    if request.method == "POST":
        form = dict()
        try:
            form = json.loads(request.body.decode("utf-8"))
        except:
            ...

        if "order_id" in form:
            order_id = form.get("order_id")

            paiement_document = PaiementDocument.objects.all().filter(order_id=order_id).first()

            if paiement_document:
                status = verifier_status(order_id)

                if not paiement_document.payer:
                    if status and status["etat"] == "OK":
                        new_document_acheter = DocumentAcheter(apprenant=paiement_document.client,
                                                               document=paiement_document.document,
                                                               montant=paiement_document.montant)
                        new_document_acheter.save()

                        paiement_document.payer = True
                        paiement_document.date_validation = datetime.datetime.date()

                        paiement_document.save()

                        response_data["etat"] = True
                        response_data["message"] = "success"
                        response_data["id"] = new_document_acheter.id

                    else:
                        response_data["message"] = status["message"]

            else:
                response_data["message"] = "operation non trouver"

    return HttpResponse(json.dumps(response_data), content_type="application/json")


@csrf_exempt
def paiement_document_callback(request, order_id):
    response_data = {'message': "requette invalide", 'etat': False}

    if request.method == "POST":
        form = dict()
        try:
            form = json.loads(request.body.decode("utf-8"))
        except:
            ...

        paiement_document = PaiementDocument.objects.all().filter(order_id=order_id).first()

        if paiement_document:
            operation = verifier_status(order_id)

            if not paiement_document.payer:
                if operation and operation["etat"] == "OK":
                    new_document_acheter = DocumentAcheter(apprenant=paiement_document.client,
                                                           document=paiement_document.document,
                                                           montant=paiement_document.montant)
                    new_document_acheter.save()

                    paiement_document.payer = True
                    paiement_document.date_validation = datetime.datetime.date()

                    paiement_document.save()

                    response_data["etat"] = True
                    response_data["message"] = "success"
                    response_data["id"] = new_document_acheter.id

                else:
                    response_data["message"] = operation["message"]

            else:
                response_data["message"] = "operation deja ternimer"

        else:
            response_data["message"] = "operation non trouver"

    return HttpResponse(json.dumps(response_data), content_type="application/json")
