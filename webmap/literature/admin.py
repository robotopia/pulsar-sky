from django.contrib import admin
from django.utils.html import format_html
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages
from django.utils.translation import ngettext
from django.db.models import Max

from . import models
from . import views

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
                'issue',
                'chapter',
                'isbn',
                'address',
                'annote',
                'booktitle',
                'edition',
                'how_published',
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
        ('Other', {
            'fields': (
                'abstract',
                'notes',
            ),
        }),
    )

    def bibtex_string_html(self, obj):
        return format_html('<pre>{}</pre>', obj.bibtex_string)

    bibtex_string_html.short_description = 'BibTeX string'


class JournalAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'abbr',)
    search_fields = ('name', 'abbr',)


admin.site.register(models.Author, AuthorAdmin)
admin.site.register(models.AuthorOrder, AuthorOrderAdmin)
admin.site.register(models.Bibtex, BibtexAdmin)
admin.site.register(models.EditorOrder, AuthorOrderAdmin)
admin.site.register(models.Journal, JournalAdmin)
