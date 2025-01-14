import json

from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from root.outil import base64_to_image

from .models import Slider


# Create your views here.

@csrf_exempt
def add_slider(request):
    response_data = {'message': "requette invalide", 'etat': False}

    if request.method == "POST":
        form = dict()
        try:
            form = json.loads(request.body.decode("utf-8"))
        except:
            ...

        if "nom" in form and "image" in form and "description" in form:
            nom = form.get("nom")
            description = form.get("description")
            image_data = form.get("image")
            image = base64_to_image(image_data)

            new_slider = Slider(nom=nom, description=description, image=image)
            new_slider.save()

            response_data["etat"] = True
            response_data["id"] = new_slider.id
            # response_data["slug"] = new_slider.slug
            response_data["message"] = "success"

        else:
            ...
        # requette invalide

    return HttpResponse(json.dumps(response_data), content_type="application/json")


@csrf_exempt
def get_slider(request):
    response_data = {'message': "requette invalide", 'etat': False}

    if request.method == "POST":
        form = dict()
        try:
            form = json.loads(request.body.decode("utf-8"))
        except:
            ...

        all_slider = Slider.objects.all()

        if len(all_slider) > 0:

            sliers = list()
            for c in all_slider:
                sliers.append(
                    {
                        "id": c.id,
                        "nom": c.nom,
                        "description": c.description,
                        "image": c.image.url if c.image else None,
                    }
                )

            response_data["etat"] = True
            response_data["donnee"] = sliers
            response_data["message"] = "success"
        else:
            response_data["message"] = "vide"

    return HttpResponse(json.dumps(response_data), content_type="application/json")

@csrf_exempt
def del_slider(request):
    response_data = {'message': "requette invalide", 'etat': False}

    if request.method == "POST":
        form = dict()
        try:
            form = json.loads(request.body.decode("utf-8"))
        except:
            ...

        if "id" in form:
            id = form.get("id")

            if id:
                slider_from_database = Slider.objects.all().filter(id=id).first()

            if not slider_from_database:
                response_data["message"] = "slider non trouvé"
            else:
                slider_from_database.delete()
                response_data["etat"] = True
                response_data["message"] = "success"

    return HttpResponse(json.dumps(response_data), content_type="application/json")

