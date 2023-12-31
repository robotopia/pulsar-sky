# Generated by Django 4.2.2 on 2023-06-23 07:04

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0018_bibtex_booktitle_bibtex_chapter_bibtex_doi_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="PulsarProperty",
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
                ("name", models.CharField(max_length=64, unique=True)),
                (
                    "unit",
                    models.CharField(
                        blank=True,
                        help_text="A string that can be parsed by astropy.units. Leave blank if dimensionless.",
                        max_length=64,
                        null=True,
                    ),
                ),
            ],
            options={
                "verbose_name_plural": "Pulsar properties",
                "ordering": ("name",),
            },
        ),
        migrations.CreateModel(
            name="PulsarPropertyMeasurement",
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
                ("value", models.CharField(max_length=1024)),
                (
                    "error",
                    models.CharField(
                        blank=True,
                        help_text='The error on "value"',
                        max_length=1024,
                        null=True,
                    ),
                ),
                (
                    "unit",
                    models.CharField(
                        blank=True,
                        help_text="A string that can be parsed by astropy.units. Leave blank if dimensionless. Must be equivalent to the parent property's unit.",
                        max_length=64,
                        null=True,
                    ),
                ),
                (
                    "bibtex",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="core.bibtex"
                    ),
                ),
                (
                    "pulsar",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="core.pulsar"
                    ),
                ),
                (
                    "pulsar_property",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="core.pulsarproperty",
                    ),
                ),
            ],
            options={
                "ordering": ("pulsar", "pulsar_property", "bibtex__year"),
            },
        ),
    ]
