from django.db import models


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

    issue = models.CharField(
        max_length=64,
        null=True,
        blank=True,
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

    bibtex = models.ForeignKey(
        "Bibtex",
        on_delete=models.CASCADE,
        related_name="author_orders",
    )

    author = models.ForeignKey(
        "Author",
        on_delete=models.CASCADE,
        related_name="author_orders",
    )

    order = models.IntegerField(
        help_text="The relative order, with lower numbers (i.e. towards neg. inf.) being first.",
    )

    def __str__(self):
        return f"{self.author} in {self.bibtex}"

    class Meta:
        ordering = ("bibtex", "order",)
        constraints = [models.UniqueConstraint(fields=['bibtex', 'order'], name='author_order')]


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
        return f"{self.author} in {self.bibtex}"

    class Meta:
        ordering = ("bibtex", "order",)
        constraints = [models.UniqueConstraint(fields=['bibtex', 'order'], name='editor_order')]

