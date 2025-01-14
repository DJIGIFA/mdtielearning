from django.urls import path

from .views import add_slider, get_slider, del_slider

urlpatterns = [
    path("add", add_slider, name="add_slider"),
    path("del", del_slider, name="add_formation"),
    path("get", get_slider, name="get_slider"),
    # path("slider/get/<int:id>", get_categorie_un, name="get_categorie_un"),
    # path("slider/set", set_categorie, name="add_formation"),
]