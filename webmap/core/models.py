from django.db import models
from django.db.models import Q
from django.utils.html import format_html

from django.core.exceptions import ValidationError

from astropy.coordinates import SkyCoord
import astropy.units as u

# Create your models here.

class ATNFFluxMeasurement(models.Model):

    pulsar = models.ForeignKey(
        "Pulsar",
        on_delete=models.CASCADE,
        related_name="atnf_flux_measurements",
    )

    freq = models.FloatField(
        help_text="The frequency in MHz",
    )

    flux = models.FloatField(
        help_text="The flux density in mJy",
    )

    error = models.FloatField(
        null=True,
        blank=True,
        help_text="The error on the flux density in mJy",
    )

    def flux_str(self):
        if self.error is not None:
            return f"{self.flux} ± {self.error} mJy"
        else:
            return f"{self.flux} mJy"

    def __str__(self):
        return f"{self.pulsar}: S{self.freq} = "#{self.flux_str}"

    class Meta:
        verbose_name = "ATNF flux measurement set"
        verbose_name_plural = "ATNF flux measurement sets"
        ordering = ("pulsar", "freq",)
        constraints = [
            models.UniqueConstraint(
                fields=["pulsar", "freq"],
                name='unique_pulsar_freq',
            ),
        ]


class Pulsar(models.Model):

    bname = models.CharField(
        max_length=16,
        null=True,
        blank=True,
    )

    jname = models.CharField(
        max_length=16,
        null=True,
        blank=True,
    )

    ra = models.FloatField(
        blank=True,
        null=True,
        verbose_name="Right ascension (deg)",
    )

    dec = models.FloatField(
        blank=True,
        null=True,
        verbose_name="Declination (deg)",
    )

    period = models.FloatField(
        blank=True,
        null=True,
        help_text="The rotation period (s).",
    )

    dm = models.FloatField(
        verbose_name="DM (pc/cm³)",
        blank=True,
        null=True,
    )

    dm_error = models.FloatField(
        verbose_name="± DM error (pc/cm³)",
        blank=True,
        null=True,
    )

    rm = models.FloatField(
        verbose_name="RM (rad/m²)",
        blank=True,
        null=True,
    )

    rm_error = models.FloatField(
        verbose_name="± RM error (rad/m²)",
        blank=True,
        null=True,
    )

    catalogue_version = models.CharField(
        max_length=64,
        blank=True,
        null=True,
    )

    spectrum_model = models.ForeignKey(
        "SpectrumModel",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )

    @property
    def DM(self):
        if self.dm is not None and self.dm_error is not None:
            return f"{self.dm} ± {self.dm_error}"
        if self.dm is not None:
            return f"{self.dm}"
        return None

    DM.fget.short_description = "DM (pc/cm³)"

    @property
    def RM(self):
        if self.rm is not None and self.rm_error is not None:
            return f"{self.rm} ± {self.rm_error}"
        if self.rm is not None:
            return f"{self.rm}"
        return None

    RM.fget.short_description = "RM (rad/m²)"

    @property
    def ra_dec(self):
        coord = SkyCoord(ra=self.ra*u.deg, dec=self.dec*u.deg)
        return coord.to_string('hmsdms', precision=1)

    ra_dec.fget.short_description = "Coordinates (RA Dec)"

    @property
    def name(self):
        if self.bname:
            return f"{self.bname}"
        elif self.jname:
            return f"{self.jname}"
        else:
            # Should never get here, due to constraint that either bname or
            # jname must be supplied
            raise Exception("Either JNAME or BNAME must be supplied.")

    def __str__(self):
        return self.name

    class Meta:
        ordering = ("ra", "dec",)
        constraints = [
            models.CheckConstraint(
                check=Q(bname__isnull=False) | Q(jname__isnull=False),
                name="name_supplied",
            ),
            models.UniqueConstraint(
                fields=['bname', 'jname'],
                name='unique_names',
            ),
        ]


class SpectrumModel(models.Model):

    name = models.CharField(
        max_length=128,
    )

    pulsar_spectra_name = models.CharField(
        max_length=128,
        help_text="The name used to identify the functional form (as implemented in pulsar_sectra).",
    )

    def __str__(self):
        return self.name

    class Meta:
        ordering = ("name",)


class SpectrumModelParameter(models.Model):

    spectrum_model = models.ForeignKey(
        "SpectrumModel",
        on_delete=models.CASCADE,
        related_name="parameters",
    )

    name = models.CharField(
        max_length=16,
    )

    def __str__(self):
        return f"{self.spectrum_model}: {self.name}"

    class Meta:
        ordering = ("spectrum_model", "name",)
        unique_together = [["spectrum_model", "name"]]


class SpectralFit(models.Model):

    pulsar = models.ForeignKey(
        "Pulsar",
        on_delete=models.CASCADE,
        related_name="fits",
    )

    parameter = models.ForeignKey(
        "SpectrumModelParameter",
        on_delete=models.CASCADE,
        related_name="fits",
    )

    value = models.FloatField()

    def __str__(self):
        return f"{self.pulsar}: {self.parameter} = {self.value}"

    class Meta:
        ordering = ("pulsar", "parameter",)
        unique_together = [["pulsar", "parameter"]]


class Bibtex(models.Model):

    BIBTEX_ARTICLE = 'AR'
    BIBTEX_BOOK = 'BO'
    BIBTEX_BOOKLET = 'BT'
    BIBTEX_CONFERENCE = 'CO'
    BIBTEX_INBOOK = 'IB'
    BIBTEX_INCOLLECTION = 'IC'
    BIBTEX_INPROCEEDINGS = 'IP'
    BIBTEX_MANUAL = 'MA'
    BIBTEX_MASTERTHESIS = 'MT'
    BIBTEX_MISC = 'MI'
    BIBTEX_PHDTHESIS = 'PT'
    BIBTEX_PROCEEDINGS = 'PR'
    BIBTEX_TECHREPORT = 'TE'
    BIBTEX_UNPUBLISHED = 'UN'

    BIBTEX_ENTRY_TYPE_CHOICES = [
        (BIBTEX_ARTICLE, 'article'),
        (BIBTEX_BOOK, 'book'),
        (BIBTEX_BOOKLET, 'booklet'),
        (BIBTEX_CONFERENCE, 'conference'),
        (BIBTEX_INBOOK, 'inbook'),
        (BIBTEX_INCOLLECTION, 'incollection'),
        (BIBTEX_INPROCEEDINGS, 'inproceedings'),
        (BIBTEX_MANUAL, 'manual'),
        (BIBTEX_MASTERTHESIS, 'masterthesis'),
        (BIBTEX_MISC, 'misc'),
        (BIBTEX_PHDTHESIS, 'phdthesis'),
        (BIBTEX_PROCEEDINGS, 'proceedings'),
        (BIBTEX_TECHREPORT, 'techreport'),
        (BIBTEX_UNPUBLISHED, 'unpublished'),
    ]

    entry_type = models.CharField(
        max_length=2,
        choices=BIBTEX_ENTRY_TYPE_CHOICES,
        default=BIBTEX_ARTICLE,
        help_text="The entry type.",
    )

    citekey = models.CharField(
        max_length=256,
        unique=True,
        help_text="The citation key for this reference.",
    )

    address = models.CharField(
        max_length=1024,
        null=True,
        blank=True,
        help_text="The address of the publisher or the institution.",
    )

    annote = models.CharField(
        max_length=1024,
        null=True,
        blank=True,
        help_text="An annotation (brief descriptive paragraph) about the reference.",
    )

    booktitle = models.CharField(
        max_length=1024,
        null=True,
        blank=True,
        help_text="The title of the book when using an inbook or incollection BibTeX entry type.",
    )

    chapter = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="The number of a chapter in a book.",
    )

    doi = models.CharField(
        max_length=256,
        null=True,
        blank=True,
        help_text="The digital object identifier (DOI) of a journal article, conference paper, book chapter or book.",
    )

    edition = models.CharField(
        max_length=16,
        null=True,
        blank=True,
        help_text="The edition number of a book.",
    )

    howpublished = models.CharField(
        max_length=256,
        null=True,
        blank=True,
        help_text="A notice for unusual publications.",
    )

    institution = models.CharField(
        max_length=256,
        null=True,
        blank=True,
        help_text="The name of the institution that published and/or sponsored the report.",
    )

    issn = models.CharField(
        max_length=64,
        null=True,
        blank=True,
        help_text="The International Standard Serial Number (ISSN) of a journal or magazine.",
    )

    isbn = models.CharField(
        max_length=64,
        null=True,
        blank=True,
        help_text="The International Standard Book Number (ISBN) of a book or report.",
    )

    journal = models.CharField(
        max_length=256,
        null=True,
        blank=True,
        help_text="The name of the journal or magazine the article was published in.",
    )

    month = models.CharField(
        max_length=16,
        null=True,
        blank=True,
        help_text="The month during the work was published or in the case of an unpublished article the month during it was written.",
    )

    note = models.CharField(
        max_length=1024,
        null=True,
        blank=True,
        help_text="Any information that might be interesting to the reader and did not fit into any of the other fields.",
    )

    number = models.CharField(
        max_length=128,
        null=True,
        blank=True,
        help_text="The number of the report for a techreport entry, and the issue number for a journal article.",
    )

    organization = models.CharField(
        max_length=256,
        null=True,
        blank=True,
        help_text="The name of the institution that organized or sponsored the conference, or that published the manual.",
    )

    pages = models.CharField(
        max_length=64,
        null=True,
        blank=True,
        help_text="Page numbers or a page range.",
    )

    publisher = models.CharField(
        max_length=256,
        null=True,
        blank=True,
        help_text="The name of the publisher.",
    )

    school = models.CharField(
        max_length=256,
        null=True,
        blank=True,
        help_text="The name of the university or degree awarding institution where the thesis was written.",
    )

    type = models.CharField(
        max_length=256,
        null=True,
        blank=True,
        help_text="A more descriptive name of the type of work.",
    )

    series = models.CharField(
        max_length=256,
        null=True,
        blank=True,
        help_text="The name of the series or set of books.",
    )

    title = models.CharField(
        max_length=1024,
        null=True,
        blank=True,
        help_text="The title of the work.",
    )

    url = models.CharField(
        max_length=1024,
        null=True,
        blank=True,
        help_text="The URL of a web page.",
    )

    volume = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="The volume number of the journal or multi-volume book.",
    )

    year = models.CharField(
        max_length=64,
        null=True,
        blank=True,
        help_text="The year the work was published or in the case of an unpublished article the year it was written.",
    )

    @property
    def author_string(self):
        author_orders = self.author_orders.all().order_by('order')
        if author_orders.exists():
            author_string = " and ".join([f"{{{author_order.author}}}" for author_order in author_orders])
            return author_string
        return None

    @property
    def editor_string(self):
        editor_orders = self.editor_orders.all().order_by('order')
        if editor_orders.exists():
            editor_string = " and ".join([f"{{{editor_order.author}}}" for editor_order in editor_orders])
            return editor_string
        return None

    @property
    def bibtex_string(self):
        bs = f"@{self.get_entry_type_display()}{{{self.citekey},\n"

        if self.address:
            bs += f'    address = "{self.address}",\n'

        if self.annote:
            bs += f'    annote = "{self.annote}",\n'

        author_string = self.author_string # To avoid running it twice
        if author_string:
            bs += f'    author = "{author_string}",\n'

        if self.booktitle:
            bs += f'    booktitle = "{self.booktitle}",\n'

        if self.chapter:
            bs += f'    chapter = "{self.chapter}",\n'

        if self.doi:
            bs += f'    doi = "{self.doi}",\n'

        if self.edition:
            bs += f'    edition = "{self.edition}",\n'

        editor_string = self.editor_string # To avoid running it twice
        if editor_string:
            bs += f'    editor = "{editor_string}",\n'

        if self.howpublished:
            bs += f'    howpublished = "{self.howpublished}",\n'

        if self.institution:
            bs += f'    institution = "{self.institution}",\n'

        if self.issn:
            bs += f'    issn = "{self.issn}",\n'

        if self.isbn:
            bs += f'    isbn = "{self.isbn}",\n'

        if self.journal:
            bs += f'    journal = "{self.journal}",\n'

        if self.month:
            bs += f'    month = "{self.month}",\n'

        if self.note:
            bs += f'    note = "{self.note}",\n'

        if self.number:
            bs += f'    number = "{self.number}",\n'

        if self.organization:
            bs += f'    organization = "{self.organization}",\n'

        if self.pages:
            bs += f'    pages = "{self.pages}",\n'

        if self.publisher:
            bs += f'    publisher = "{self.publisher}",\n'

        if self.school:
            bs += f'    school = "{self.school}",\n'

        if self.type:
            bs += f'    type = "{self.type}",\n'

        if self.series:
            bs += f'    series = "{self.series}",\n'

        if self.title:
            bs += f'    title = "{self.title}",\n'

        if self.url:
            bs += f'    url = "{self.url}",\n'

        if self.volume:
            bs += f'    volume = "{self.volume}",\n'

        if self.year:
            bs += f'    year = "{self.year}",\n'

        bs += "}"

        return bs

    def __str__(self):
        return self.citekey

    class Meta:
        verbose_name = "BibTeX"
        verbose_name_plural = "BibTeX"
        ordering = ("citekey",)


class Author(models.Model):

    first = models.CharField(
        max_length=64,
        help_text="First name or given names",
    )

    last = models.CharField(
        max_length=64,
        help_text="Last name or family name",
    )

    von = models.CharField(
        max_length=16,
        null=True,
        blank=True,
        help_text="A particle (e.g. de, de la, der, van, von)",
    )

    jr = models.CharField(
        max_length=16,
        null=True,
        blank=True,
        help_text="A suffix (e.g. Jr., Sr., III)"
    )

    def __str__(self):
        if self.von and self.jr:
            return f"{self.von} {self.last}, {self.jr}, {self.first}"

        if self.jr:
            return f"{self.last}, {self.jr}, {self.first}"

        if self.von:
            return f"{self.von} {self.last}, {self.first}",

        return f"{self.last}, {self.first}"

    class Meta:
        ordering = ("last", "first", "von", "jr",)


class AuthorOrder(models.Model):

    author = models.ForeignKey(
        "Author",
        on_delete=models.CASCADE,
        related_name="author_orders",
    )

    bibtex = models.ForeignKey(
        "Bibtex",
        on_delete=models.CASCADE,
        related_name="author_orders",
    )

    order = models.IntegerField(
        help_text="The relative order, with lower numbers (i.e. towards neg. inf.) being first.",
    )

    def __str__(self):
        return "{self.author} in {self.bibtex}"

    class Meta:
        ordering = ("bibtex", "order",)


class EditorOrder(models.Model):

    author = models.ForeignKey(
        "Author",
        on_delete=models.CASCADE,
        related_name="editor_orders",
    )

    bibtex = models.ForeignKey(
        "Bibtex",
        on_delete=models.CASCADE,
        related_name="editor_orders",
    )

    order = models.IntegerField(
        help_text="The relative order, with lower numbers (i.e. towards neg. inf.) being first.",
    )

    def __str__(self):
        return "{self.author} in {self.bibtex}"

    class Meta:
        ordering = ("bibtex", "order",)


class PulsarProperty(models.Model):

    name = models.CharField(
        max_length=64,
        unique=True,
    )

    unit = models.CharField(
        null=True,
        blank=True,
        max_length=64,
        help_text="A string that can be parsed by astropy.units. Leave blank if dimensionless.",
    )

    def clean(self):

        if self.unit:
            try:
                unit = u.Unit(self.unit)
            except:
                raise ValidationError(f'Unable to interpret {self.unit} as a valid Astropy unit')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Pulsar properties"
        ordering = ("name",)


class PulsarPropertyMeasurement(models.Model):

    pulsar = models.ForeignKey(
        "Pulsar",
        on_delete=models.CASCADE,
    )

    pulsar_property = models.ForeignKey(
        "PulsarProperty",
        on_delete=models.CASCADE,
    )

    value = models.CharField(
        max_length=1024,
    )

    error = models.CharField(
        null=True,
        blank=True,
        max_length=1024,
        help_text="The error on \"value\"",
    )

    unit = models.CharField(
        null=True,
        blank=True,
        max_length=64,
        help_text="A string that can be parsed by astropy.units. Leave blank if dimensionless. Must be equivalent to the parent property's unit.",
    )

    bibtex = models.ForeignKey(
        "Bibtex",
        on_delete=models.CASCADE,
    )

    def clean(self):

        if self.unit:
            try:
                u1 = u.Unit(self.unit)
            except:
                raise ValidationError(f'Unable to interpret {self.unit} as a valid Astropy unit')

            u2 = u.Unit(self.pulsar_property.unit)
            if not u1.is_equivalent(u2):
                raise ValidationError(f'The unit "{self.unit}" must be dimensionally equivalent to {self.pulsar_property.unit}')

    def __str__(self):
        return f"{self.pulsar_property} of {self.pulsar} ({self.bibtex})"

    class Meta:
        ordering = ("pulsar", "pulsar_property", "bibtex__year",)
