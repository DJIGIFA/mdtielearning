from django.urls import path

from .views import instructeur_index, instructeur_formation_liste, instructeur_add_formation, \
    instructeur_edit_formation, instructeur_detaille_formation, instructeur_edit_chapitre, \
    instructeur_detaille_chapitre, instructeur_suppression_de_la_video, instructeur_edit_qcm, instructeur_detaille_qcm, \
    instructeur_supprimer_question_qcm, instructeur_detaille_question, delete_reponse_qcm

urlpatterns = [
    path('', instructeur_index, name='instructeur_index'),
    path('instructeur-formation-liste', instructeur_formation_liste, name='instructeur_formation_liste'),
    path('instructeur-formation-edit/<int:id>', instructeur_edit_formation, name='instructeur_edit_formation'),
    path('instructeur-formation-detaille/<int:id>', instructeur_detaille_formation, name='instructeur_detaille_formation'),
    path('instructeur-formation-chapitre-edit/<int:id>', instructeur_edit_chapitre, name='instructeur_edit_chapitre'),
    path('instructeur-formation-chapitre-detaill/<int:id>', instructeur_detaille_chapitre, name='instructeur_detaille_chapitre'),
    path('instructeur-formation-chapitre-video/suppression/<int:id>', instructeur_suppression_de_la_video, name='instructeur_suppression_de_la_video'),
    path('instructeur-formation-qcm/edite/<int:id>', instructeur_edit_qcm, name='instructeur_edit_qcm'),
    path('instructeur-formation-qcm/detail/<int:id>', instructeur_detaille_qcm, name='instructeur_detaille_qcm'),
    path('instructeur/qcm/del/<int:id>', instructeur_supprimer_question_qcm, name='instructeur_supprimer_question_qcm'),
    path('qcm/question/detaille/<int:id>', instructeur_detaille_question, name='instructeur_detaille_question'),
    path('qcm/question/reponse/del/<int:id>', delete_reponse_qcm, name='delete_reponse_qcm'),
    path('instructeur-add-formation', instructeur_add_formation, name='instructeur_add_formation'),
]