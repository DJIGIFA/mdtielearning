from django.shortcuts import render

from formation.models import Categorie


def index(request):
    all_categorie = Categorie.objects.all()

    context = {
        'all_categorie': all_categorie,
    }
    return render(request, 'index.html', context=context)