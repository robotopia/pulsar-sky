"""
URL configuration for webmap project.

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
from django.contrib import admin
from django.urls import re_path, path, include
from django.conf import settings
from django.conf.urls.static import static

from . import views

urlpatterns = [
    re_path(r'^map/$', views.map, name='map'),
    re_path(r'^import_atnf/$', views.import_atnf, name='import_atnf'),
    re_path(r'^update_atnf_fluxes/$', views.update_atnf_fluxes, name='update_atnf_fluxes'),
    re_path(r'^import_spectra/$', views.import_spectra, name='import_spectra'),
]
