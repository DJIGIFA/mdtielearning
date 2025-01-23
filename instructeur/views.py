from django.contrib import messages
from django.shortcuts import render, redirect
from django.urls import reverse

from formation.models import Formation, SousCategorie, Chapitre, Video, Qcm


# Create your views here.


def instructeur_index(request):


    return render(request, "instructeur/instructeur_index.html")


def instructeur_formation_liste(request):

    all_formations = Formation.objects.all().filter(instructeur=request.user)

    context = {
        "all_formations": all_formations,
    }

    return render(request, "instructeur/instructeur_formation_liste.html",context=context)




def instructeur_add_formation(request):
    sous_categories = SousCategorie.objects.all()


    if request.method == "POST":
        form = request.POST
        nom= form.get("nom")

        miniature = request.FILES.get("miniature")

        prix = form.get("prix")
        sous_categorie_id = form.get("sous_categorie_id")

        sous_categorie = SousCategorie.objects.all().filter(id=sous_categorie_id).first()

        nombre_heur = form.get("nombre_heur")
        description = form.get("description")
        prerequis = form.get("prerequis")
        profile_destine = form.get("profile_destine")
        objectif_du_cours = form.get("objectif_du_cours")

        # CREATION DE LA FORMATION

        new_formation = Formation(
            nom = nom,
            prix = prix,
            sous_categorie = sous_categorie,
            nombre_heur = nombre_heur,
            description = description,
            prerequis = prerequis,
            profile_destine = profile_destine,
            objectif_du_cours = objectif_du_cours,
            miniature=miniature,
            instructeur=request.user
        )

        new_formation.save()

        messages.success(request, "Formation ajouter")

        return redirect(reverse("instructeur_formation_liste"))


    context = {
        "sous_categories": sous_categories,
    }
    return render(request, "instructeur/instructeur_add_formation.html",context=context)



def instructeur_edit_formation(request, id):

    formation = Formation.objects.all().filter(id=id).first()

    sous_categories = SousCategorie.objects.all()

    if request.method == "POST":
        form = request.POST
        nom = form.get("nom")


        modifier = False
        if nom != formation.nom:
            if nom != formation.nom:
                formation.nom = nom
                modifier = True

        if "miniature" in request.FILES:
            miniature = request.FILES["miniature"]
            formation.miniature = miniature
            modifier = True

        if "prix" in form:
            prix = int(form.get("prix").split(",")[0])
            if int(prix) != int(formation.prix):
                formation.prix = prix
                modifier = True

        sous_categorie_id = form.get("sous_categorie_id")

        if sous_categorie_id != formation.sous_categorie.id:
            sous_categorie = SousCategorie.objects.all().filter(id=sous_categorie_id).first()
            formation.sous_categorie = sous_categorie
            modifier = True

        if "nombre_heur" in form:
            nombre_heur = int(form.get("nombre_heur").split(",")[0])
            if nombre_heur != formation.nombre_heur:
                formation.nombre_heur = nombre_heur

        if "description" in form:
            description = form.get("description")
            if description != formation.description:
                formation.description = description
                modifier = True

        if "prerequires" in form:
            prerequis = form.get("prerequires")

            if prerequis != formation.prerequis:
                formation.prerequis = prerequis
                modifier = True

        if modifier:
            formation.save()
            messages.success(request, "Modifier")


    context = {
        "formation": formation,
        "sous_categories":sous_categories
    }

    return render(request, "instructeur/instructeur_edit_formation.html", context=context)



def instructeur_detaille_formation(request,id):
    formation = Formation.objects.all().filter(id=id).first()

    if request.method == "POST":
        form = request.POST

        if "add_chapitre" in form:
            nom = form.get("nom")

            new_chapitre = Chapitre(nom=nom,formation=formation)
            new_chapitre.save()
            messages.success(request, "Chapitre ajouter")

        if "add_qcm" in form:
            nom = form.get("nom")
            description = form.get("description")
            duree = form.get("duree")

            new_qcm = Qcm(nom=nom,description=description,duree=duree,formation=formation)
            new_qcm.save()

            messages.success(request, "Qcm ajouter")


    sous_categories = SousCategorie.objects.all()
    context = {
        "formation": formation,
        "sous_categories":sous_categories
    }

    return render(request, "instructeur/instructeur_detaille_formation.html",context=context)






def instructeur_edit_chapitre(request,id):
    chapitre = Chapitre.objects.all().filter(id=id).first()

    if request.method == "POST":
        form = request.POST

        modifier = False
        nom = form.get("nom")


        if nom != chapitre.nom:
            chapitre.nom = nom
            modifier = True


        if "ordre" in form:
            ordre = int(form.get("ordre"))
            if ordre != chapitre.ordre:
                chapitre.ordre = ordre
                modifier = True


        if modifier:
            chapitre.save()
            messages.success(request, "Chapitre Modifier")

        return redirect(reverse('instructeur_detaille_formation', kwargs={'id': chapitre.formation.id}))


    context = {
        "chapitre": chapitre,
    }

    return render(request, "instructeur/instructeur_edit_chapitre.html",context=context)



def instructeur_detaille_chapitre(request,id):
    chapitre = Chapitre.objects.all().filter(id=id).first()

    if request.method == "POST":
        form = request.POST
        nom = form.get("nom")
        duree = form.get("duree")
        ordre = form.get("ordre")

        video = request.FILES.get("video")

        video = Video(
            nom=nom,
            duree=duree,
            ordre=ordre,
            video=video,
            chapitre=chapitre
        )

        video.save()
        messages.success(request, "Video ajouter")

    context = {
        "chapitre": chapitre,
    }

    return render(request, "instructeur/instructeur_detaille_chapitre.html",context=context)





def instructeur_suppression_de_la_video(request,id):
    video = Video.objects.all().filter(id=id).first()

    if video:
        video.delete()
        messages.success(request, "Video supprimée")
    else:
        messages.warning(request,"Vidéo non trouver")



    return redirect(reverse('instructeur_detaille_chapitre', kwargs={'id': video.chapitre.id}))


def instructeur_edit_qcm(request, id):

    qcm = Qcm.objects.all().filter(id=id).first()

    if request.method == "POST":
        form = request.POST
        modifier = False
        nom = form.get("nom")

        if nom != qcm.nom:
            qcm.nom = nom
            modifier = True

        if "description" in form:
            description = form.get("description")

            if description != qcm.description:
                qcm.description = description
                modifier = True

        if "duree" in form:
            duree = int(form.get("duree"))

            if duree != qcm.duree:
                qcm.duree = duree
                modifier = True

        if modifier:
            qcm.save()
            messages.success(request, "Qcm Modifier")

            return redirect(reverse('instructeur_detaille_formation', kwargs={'id': qcm.formation.id}))



    return render(request,"instructeur/instructeur_edit_qcm.html",context={"qcm":qcm})



def instructeur_detaille_qcm(request, id):

    qcm = Qcm.objects.all().filter(id=id).first()

    if request.method == "POST":
        ...


    return render(request,"instructeur/instructeur_detaille_qcm.html",context={"qcm":qcm})


def instructeur_quizz(request):

    return render(request, "instructeur/instructeur_quizz.html")