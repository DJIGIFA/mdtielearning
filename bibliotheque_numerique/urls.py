from django.urls import path

from .views import add_categorie, del_categorie, get_categorie, \
    set_categorie, add_auteur, del_auteur, get_auteur, set_auteur, add_livre, del_livre, get_livre, set_livre, \
    get_categorie_un, get_auteur_un, get_livre_un

urlpatterns = [

    path("categorie/add", add_categorie, name="add_bibliotheque"),
    path("categorie/del", del_categorie, name="add_bibliotheque"),
    path("categorie/get", get_categorie, name="add_bibliotheque"),
    path("categorie/get/<int:id>", get_categorie_un, name="add_bibliotheque"),
    path("categorie/set", set_categorie, name="add_bibliotheque"),

    path("auteur/add", add_auteur, name="add_bibliotheque"),
    path("auteur/del", del_auteur, name="add_bibliotheque"),
    path("auteur/get", get_auteur, name="add_bibliotheque"),
    path("auteur/get/<int:id>", get_auteur_un, name="add_bibliotheque"),
    path("auteur/set", set_auteur, name="add_bibliotheque"),

    path("livre/add", add_livre, name="add_bibliotheque"),
    path("livre/del", del_livre, name="add_bibliotheque"),
    path("livre/get", get_livre, name="add_bibliotheque"),
    path("livre/get/<int:id>", get_livre_un, name="add_bibliotheque"),
    path("livre/set", set_livre, name="add_bibliotheque"),

]
