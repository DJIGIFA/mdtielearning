from django.urls import path

from .views import add_type_sujet, get_type_sujet, get_type_sujet_un, del_type_sujet, add_niveau_sujet, \
    get_niveau_sujet, get_un_niveau_sujet, del_niveau_sujet, add_matiere_sujet, get_matiere_sujet, get_matiere_sujet_un, \
    del_matiere_sujet, add_document, del_document, get_document_all, get_document_params, get_document_un, set_document, \
    add_pays_sujet, del_pays_sujet, get_pays_sujet_un, get_pays_sujet, ordre_paiement_document, \
    paiement_document_callback, pay_document_get_historique, pay_document_verifier, set_type_sujet, set_niveau_sujet, \
    set_matiere_sujet

urlpatterns = [
    path("type/add", add_type_sujet, name="add_type_sujet"),
    path("type/get", get_type_sujet, name="get_type_sujet"),
    path("type/set", set_type_sujet, name="get_type_sujet"),
    path("type/get/<int:id>", get_type_sujet_un, name="get_type_sujet_un"),
    path("type/del", del_type_sujet, name="del_type_sujet"),

    path("niveau/add", add_niveau_sujet, name="add_niveau_sujet"),
    path("niveau/get", get_niveau_sujet, name="get_niveau_sujet"),
    path("niveau/set", set_niveau_sujet, name="get_niveau_sujet"),
    path("niveau/get/<int:id>", get_un_niveau_sujet, name="get_un_niveau_sujet"),
    path("niveau/del", del_niveau_sujet, name="del_niveau_sujet"),

    path("matiere/add", add_matiere_sujet, name="add_matiere_sujet"),
    path("matiere/get", get_matiere_sujet, name="get_matiere_sujet"),
    path("matiere/set", set_matiere_sujet, name="get_matiere_sujet"),
    path("matiere/get/<int:id>", get_matiere_sujet_un, name="get_matiere_sujet_un"),
    path("matiere/del", del_matiere_sujet, name="del_matiere_sujet"),

    path("pays/add", add_pays_sujet, name="add_pays_sujet"),
    path("pays/get", get_pays_sujet, name="get_pays_sujet"),
    path("pays/get/<int:id>", get_pays_sujet_un, name="get_pays_sujet_un"),
    path("pays/del", del_pays_sujet, name="del_pays_sujet"),

    path("document/add", add_document, name="add_document"),
    path("document/set", set_document, name="set_document"),
    path("document/get/<int:id>", get_document_un, name="get_document_un"),
    path("document/get-all", get_document_all, name="get_document_all"),
    path("document/get", get_document_params, name="get_document_params"),
    path("document/del", del_document, name="del_document"),

    # pour le paiement
    path("pay", ordre_paiement_document, name="ordre_paiement_document"),
    path("pay/get-historique", pay_document_get_historique, name="pay_document_get_historique"),
    path("pay-verifier",pay_document_verifier,name="pay_document_verifier"),

    path("callback/<str:order_id>/validation/achat-document", paiement_document_callback,
         name="paiement_document_callback"),

]
