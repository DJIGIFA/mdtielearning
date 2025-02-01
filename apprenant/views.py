from django.contrib import messages
from django.shortcuts import render, redirect
from django.urls import reverse

from formation.models import Cour, Formation, PaiementFormation
from root.code_paiement import formation_order_id_len
from root.outil import get_order_id, verifier_numero, paiement_orange, verifier_status, paiement_moov, sama_pay


# Create your views here.

def apprenant_index(request):
    if not request.user.is_authenticated:
        return redirect(reverse("web_connexion"))


    nombre_de_cour = len(Cour.objects.all().filter(apprenant=request.user))

    context = {
        "nombre_de_cour": nombre_de_cour,
    }


    return render(request, "apprenant/apprenant_index.html", context=context)



def apprenant_mes_cours(request):

    # TODO securité
    if not request.user.is_authenticated:
        return redirect(reverse("web_connexion"))

    all_cours = Cour.objects.all().filter(apprenant=request.user)

    context = {
        "all_cours": all_cours,
    }

    return render(request, "apprenant/apprenant_mes_cours.html",context=context)




def apprenant_paiement(request):



    return render(request, "apprenant/apprenant_paiement.html")






def apprenant_achat(request,id_formation):

    formation = Formation.objects.all().filter(id=id_formation).first()


    if request.method == "POST":
        moyen_paiement = request.POST.get("moyen_paiement")
        print(request.POST.get("moyen_paiement"))
        if moyen_paiement != "Carte Visa":
            return redirect(reverse('apprenant_achat_mobile', kwargs=
            {
                'id_formation':id_formation,
                'moyen_paiement':moyen_paiement
            }))
        else:
            return redirect(reverse('apprenant_achat_visa', kwargs=
            {
                'id_formation':id_formation
            }
            ))

    context = {
        "formation": formation,
    }

    return render(request, "apprenant/apprenant_achat.html", context=context)


def apprenant_achat_mobile(request,id_formation,moyen_paiement):
    formation = Formation.objects.all().filter(id=id_formation).first()

    if request.method == "POST":
        numero_telephone = request.POST.get("numero_telephone")

        client = request.user
        montant = formation.prix
        description = formation.nom
        order_id = get_order_id(formation_order_id_len)

        while PaiementFormation.objects.all().filter(order_id=order_id).first():
            order_id = get_order_id(formation_order_id_len)


        tm = reverse('paiement_formation_callback', kwargs={'order_id': order_id})
        notify_url = f"{request.scheme}://{request.get_host()}{tm}"

        operation = None
        ordre_donner = False
        # TODO verifier si le montant est supperieur à un minimum ?
        print(notify_url)
        # Paiement par orange money
        if moyen_paiement == "Orange Money":
            # paiement orange
            if verifier_numero(numero_telephone):
                operation = paiement_orange(
                    montant=montant,
                    numero=numero_telephone,
                    order_id=order_id,
                    notify_url=notify_url
                )

                if operation:
                    if operation["etat"] == "OK":
                        ordre_donner = True

                else:
                    messages.error(request,operation["message"])
            else:
                messages.error(request,"numero telephone invalide")



        elif moyen_paiement == "Moov Money":

            if verifier_numero(numero_telephone):
                operation = paiement_moov(montant=montant,
                                          numero=numero_telephone,
                                          order_id=order_id,
                                          description=f"{description}",
                                          remarks="remarks",
                                          notify_url=notify_url)

                if operation and operation["status"] == 0 and operation["etat"] == "OK":
                    ordre_donner = True
                    # ---
                else:
                    messages.error(request, "Une erreur s'est produite")

                    try:
                        if "message" in operation:
                            messages.error(request, operation["message"])

                    except:
                        ...

            else:
                messages.error(request,"numero invalide")

        elif moyen_paiement == "Sama Money":

            if verifier_numero(numero_telephone):
                operation = sama_pay(montant=montant,
                                     order_id=order_id,
                                     numero=numero_telephone,
                                     description=f"{description}",
                                     notify_url=notify_url)
                if operation and operation["etat"] == "OK" and operation["status"] == 1:
                    ordre_donner = True
                    # ----
                else:
                    messages.error(request, operation["message"])
            else:
                messages.error(request, "numero invalide")

        if not ordre_donner:
            # verification
            operation = verifier_status(order_id)

            if operation and "message" in operation and "operator" in operation:
                ordre_donner = True

        if ordre_donner:
            new_paiement = PaiementFormation(order_id=order_id,
                                             moyen_paiement=moyen_paiement,
                                             montant=montant,
                                             formation=formation,
                                             client=client,
                                             numero=numero_telephone,)

            new_paiement.save()
            messages.success(request, "Paiement initier \n veillez terminer le processus sur votre téléphone")

    context = {
        "moyen_paiement": moyen_paiement,
        "formation": formation,
    }

    return render(request, "apprenant/apprenant_achat_mobile.html", context=context)

def apprenant_achat_visa(request,id_formation):

    formation = Formation.objects.all().filter(id=id_formation).first()



    context = {
        "formation": formation,
    }

    return render(request, "apprenant/apprenant_achat_visa.html", context=context)

def apprenant_detaille_formation(request,id_cour):
    cour = Cour.objects.all().filter(id=id_cour).first()

    context = {
        "cour": cour,
    }

    return render(request, "apprenant/apprenant_detaille_formation.html", context=context)


