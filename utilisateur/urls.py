from django.urls import path

from .views import api_user_login, api_user_register, api_user_get_profil, api_user_set_profil, api_user_get, \
    add_universiter, del_universiter, get_universiter, get_universiter_un, set_universiter, web_connexion, \
    web_inscription, web_deconnexion, admin_index

urlpatterns = [

    # API URL
    path("connexion", api_user_login, name="connexion"),
    path("inscription", api_user_register, name="api_user_register"),
    path("profile/get/<int:id>", api_user_get_profil, name="api_user_get_profil"),
    path("profile/set", api_user_set_profil, name="api_user_set_profil"),
    path("get", api_user_get, name="api_user_get"),
    
    path("universiter/add", add_universiter, name="add_formation"),
    path("universiter/del", del_universiter, name="add_formation"),
    path("universiter/get", get_universiter, name="add_formation"),
    path("universiter/get/<int:id>", get_universiter_un, name="get_categorie_un"),
    path("universiter/set", set_universiter, name="add_formation"),



    # Web url


    path("web-connexion", web_connexion, name="web_connexion"),
    path("web-de-connexion", web_deconnexion, name="web_deconnexion"),
    path("web-inscription", web_inscription, name="web_inscription"),


    path("web-admin-index", admin_index, name="admin_index"),


]
