from django.contrib import admin
from django.utils.html import format_html
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages
from django.utils.translation import ngettext
from django.db.models import Max

from . import models
from . import views

from astropy.coordinates import SkyCoord
import astropy.units as u

# Register your models here.
class PulsarAdmin(admin.ModelAdmin):
    list_display = ('id', '__str__', 'ra_dec', 'period', 'DM', 'RM', 'spectrum_model',)
    list_filter = ('spectrum_model',)

    def DM(self, obj):
        if obj.dm is not None and obj.dm_error is not None:
            return f"{obj.dm} ± {obj.dm_error}"
        if obj.dm is not None:
            return f"{obj.dm}"
        return ""

    def RM(self, obj):
        if obj.rm is not None and obj.rm_error is not None:
            return f"{obj.rm} ± {obj.rm_error}"
        if obj.rm is not None:
            return f"{obj.rm}"
        return ""

    def ra_dec(self, obj):
        coord = SkyCoord(ra=obj.ra*u.deg, dec=obj.dec*u.deg)
        return coord.to_string('hmsdms', precision=1)

class SpectrumModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'pulsar_spectra_name',)

class SpectrumModelParameterAdmin(admin.ModelAdmin):
    list_display = ('id', 'spectrum_model', 'name',)

class SpectralFitAdmin(admin.ModelAdmin):
    list_display = ('id', 'pulsar', 'model_name', 'parameter', 'value',)

    def model_name(self, obj):
        return f"{obj.parameter.spectrum_model}"


admin.site.register(models.Pulsar, PulsarAdmin)
admin.site.register(models.SpectrumModel, SpectrumModelAdmin)
admin.site.register(models.SpectrumModelParameter, SpectrumModelParameterAdmin)
admin.site.register(models.SpectralFit, SpectralFitAdmin)
