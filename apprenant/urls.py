from django.urls import path


from .views import apprenant_index, apprenant_mes_cours, apprenant_paiement, apprenant_achat, apprenant_achat_visa, \
    apprenant_achat_mobile, apprenant_detaille_formation

urlpatterns = [
    path("index",apprenant_index, name="apprenant_index"),
    path("mes-cours",apprenant_mes_cours, name="apprenant_mes_cours"),
    path("mes-cours/detail/<int:id_cour>",apprenant_detaille_formation, name="apprenant_detaille_formation"),
    path("paiement",apprenant_paiement, name="apprenant_paiement"),
    path("apprenant_achat/<int:id_formation>",apprenant_achat, name="apprenant_achat"),
    path("apprenant_achat_visa/<int:id_formation>",apprenant_achat_visa, name="apprenant_achat_visa"),
    path("apprenant_achat_mobile/<int:id_formation>/<str:moyen_paiement>",apprenant_achat_mobile, name="apprenant_achat_mobile"),
]