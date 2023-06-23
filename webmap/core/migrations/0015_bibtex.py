# Generated by Django 4.2.2 on 2023-06-23 04:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0014_alter_spectrummodel_pulsar_spectra_name"),
    ]

    operations = [
        migrations.CreateModel(
            name="Bibtex",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "entry_type",
                    models.CharField(
                        choices=[
                            ("AR", "article"),
                            ("BO", "book"),
                            ("BT", "booklet"),
                            ("CO", "conference"),
                            ("IB", "inbook"),
                            ("IC", "incollection"),
                            ("IP", "inproceedings"),
                            ("MA", "manual"),
                            ("MT", "masterthesis"),
                            ("MI", "misc"),
                            ("PT", "phdthesis"),
                            ("PR", "proceedings"),
                            ("TE", "techreport"),
                            ("UN", "unpublished"),
                        ],
                        default="AR",
                        help_text="The entry type.",
                        max_length=2,
                    ),
                ),
                (
                    "citekey",
                    models.CharField(
                        help_text="The citation key for this reference.",
                        max_length=256,
                        unique=True,
                    ),
                ),
                (
                    "address",
                    models.CharField(
                        blank=True,
                        help_text="The address of the publisher or the institution.",
                        max_length=1024,
                        null=True,
                    ),
                ),
                (
                    "annote",
                    models.CharField(
                        blank=True,
                        help_text="An annotation (brief descriptive paragraph) about the reference.",
                        max_length=1024,
                        null=True,
                    ),
                ),
            ],
            options={
                "verbose_name": "BibTeX",
                "verbose_name_plural": "BibTeX",
                "ordering": ("citekey",),
            },
        ),
    ]
