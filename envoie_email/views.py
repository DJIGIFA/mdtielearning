import json

from django.core.mail import send_mail
from django.http import HttpResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt

from root.settings import EMAIL_HOST_USER


# Create your views here.

@csrf_exempt
def envoie_email(request):
    response_data = {'message': "requette invalide", 'etat': False}

    # send_mail(
    #     sujet,
    #     message,
    #     EMAIL_HOST_USER
    #     ,
    #     email_liste,
    #     html_message=html_message)

    form = dict()
    try:
        form = json.loads(request.body.decode("utf-8"))
    except:
        ...

    if request.method == "POST" and "email_liste" in form and "message" in form and "sujet" in form:
        email_liste = form.get("email_liste").split(",")
        sujet = form.get("sujet")
        message = form.get("message")

        html_message = render_to_string('mail/mail.html',
                                        context={"message": message})

        try:
            send_mail(
                sujet,
                message,
                EMAIL_HOST_USER
                ,
                email_liste,
                html_message=html_message
            )

            response_data["etat"] = True
            response_data["message"] = "success"
        except:
            response_data["message"] = "Une erreur s'est produtie"

    return HttpResponse(json.dumps(response_data), content_type="application/json")