from django.contrib import admin
from django.utils.html import format_html
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages
from django.utils.translation import ngettext
from django.db.models import Max

from . import models
from . import views

class ATNFFluxMeasurementAdmin(admin.ModelAdmin):
    list_display = ('id', 'pulsar', 'freq', 'flux_str',)
    search_fields = ('pulsar__bname', 'pulsar__jname')
    list_filter = ('freq',)

class AuthorAdmin(admin.ModelAdmin):
    list_display = ('id', '__str__')
    search_fields = ('last', 'first', 'von', 'jr',)

class AuthorOrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'bibtex', 'order', 'author',)
    list_filter = (
        ('bibtex', admin.RelatedOnlyFieldListFilter),
        ('author', admin.RelatedOnlyFieldListFilter),
    )

class BibtexAdmin(admin.ModelAdmin):
    list_display = ('id', 'entry_type', 'citekey', 'author_string', 'title',)
    search_fields = ('address', 'annote',)
    readonly_fields = ('bibtex_string_html',)
    list_filter = (
        'entry_type',
        ('author_orders__author', admin.RelatedOnlyFieldListFilter),
    )
    fieldsets = (
        (None, {
            'fields': (
                'bibtex_string_html',
                'entry_type',
                'citekey',
            ),
        }),
        ('BibTeX fields', {
            'fields': (
                'title',
                'journal',
                'volume',
                'pages',
                'year',
                'month',
                'doi',
                'url',
                'chapter',
                'isbn',
                'address',
                'annote',
                'booktitle',
                'edition',
                'howpublished',
                'institution',
                'issn',
                'note',
                'number',
                'organization',
                'publisher',
                'school',
                'type',
                'series',
            ),
            #'classes': ('collapse',),
        }),
    )

    def bibtex_string_html(self, obj):
        return format_html('<pre>{}</pre>', obj.bibtex_string)

    bibtex_string_html.short_description = 'BibTeX string'

class PulsarAdmin(admin.ModelAdmin):
    list_display = ('id', '__str__', 'ra_dec', 'period', 'DM', 'RM', 'spectrum_model', 'fit_link', 'pulsar_page_link',)
    list_filter = ('spectrum_model',)
    search_fields = ('bname', 'jname')

    def fit_link(self, obj):
        if obj.spectrum_model:
            url = reverse('admin:core_spectralfit_changelist') + f'?pulsar__id__exact={obj.id}'
            return format_html('<a href="{url}">Go to fit</a>', url=url)
        else:
            return ""

    def pulsar_page_link(self, obj):
        url = reverse('pulsar_view', kwargs={"pk": obj.pk})
        return format_html('<a href="{url}">{name} link</a>', url=url, name=obj.name)

    actions = ['set_atnf_power_laws', 'set_atnf_power_laws_force']

    @admin.action(description="Set to ATNF simple power law")
    def set_atnf_power_laws(self, request, queryset):

        num_set = 0

        for pulsar in queryset.all():

            if views.set_atnf_power_law(pulsar):
                num_set += 1

        self.message_user(
            request,
            ngettext(
                "%d pulsar updated.",
                "%d pulsars updated.",
                num_set,
            ) % num_set,
            messages.SUCCESS,
        )

    @admin.action(description="Set to ATNF simple power law (force)")
    def set_atnf_power_laws_force(self, request, queryset):

        num_set = 0

        for pulsar in queryset.all():

            if views.set_atnf_power_law(pulsar, overwrite=True):
                num_set += 1

        self.message_user(
            request,
            ngettext(
                "%d pulsar updated.",
                "%d pulsars updated.",
                num_set,
            ) % num_set,
            messages.SUCCESS,
        )

class PulsarPropertyAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'symbol', 'unit',)

class PulsarPropertyMeasurementAdmin(admin.ModelAdmin):
    list_display = ('id', 'pulsar', 'pulsar_property', 'value_display', 'unit', 'bibtex',)
    list_filter = (
        ('pulsar', admin.RelatedOnlyFieldListFilter),
        ('pulsar_property', admin.RelatedOnlyFieldListFilter),
    )

class SpectrumModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'pulsar_spectra_name',)

class SpectrumModelParameterAdmin(admin.ModelAdmin):
    list_display = ('id', 'spectrum_model', 'name',)

class SpectralFitAdmin(admin.ModelAdmin):
    list_display = ('id', 'pulsar', 'parameter', 'value',)
    search_fields = ('pulsar__bname', 'pulsar__jname')

    def model_name(self, obj):
        return f"{obj.parameter.spectrum_model}"


admin.site.register(models.ATNFFluxMeasurement, ATNFFluxMeasurementAdmin)
admin.site.register(models.Author, AuthorAdmin)
admin.site.register(models.AuthorOrder, AuthorOrderAdmin)
admin.site.register(models.Bibtex, BibtexAdmin)
admin.site.register(models.EditorOrder, AuthorOrderAdmin)
admin.site.register(models.Pulsar, PulsarAdmin)
admin.site.register(models.PulsarProperty, PulsarPropertyAdmin)
admin.site.register(models.PulsarPropertyMeasurement, PulsarPropertyMeasurementAdmin)
admin.site.register(models.SpectrumModel, SpectrumModelAdmin)
admin.site.register(models.SpectrumModelParameter, SpectrumModelParameterAdmin)
admin.site.register(models.SpectralFit, SpectralFitAdmin)
