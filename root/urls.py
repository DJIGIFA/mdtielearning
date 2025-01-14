"""
URL configuration for root project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from root import settings
from .views import index

# from django.views.generic import TemplateView

urlpatterns = [
                  path('admin/', admin.site.urls),
                  path('', index, name='index'),
                  # path('', TemplateView.as_view(template_name='index.html')),
                  # path('<path:path>', TemplateView.as_view(template_name='index.html')),
                  path('utilisateur/', include("utilisateur.urls")),
                  path('formation/', include("formation.urls")),
                  path('slider/', include("slide.urls")),
                  path('mail/', include("envoie_email.urls")),
                  path('ancien-sujet/', include("ancien_sujet.urls")),
                  path('bibliotheque-numerique/', include("bibliotheque_numerique.urls")),

              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
