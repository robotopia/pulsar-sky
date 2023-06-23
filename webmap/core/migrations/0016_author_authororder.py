# Generated by Django 4.2.2 on 2023-06-23 04:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0015_bibtex"),
    ]

    operations = [
        migrations.CreateModel(
            name="Author",
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
                    "first",
                    models.CharField(
                        help_text="First name or given names", max_length=64
                    ),
                ),
                (
                    "last",
                    models.CharField(
                        help_text="Last name or family name", max_length=64
                    ),
                ),
                (
                    "von",
                    models.CharField(
                        blank=True,
                        help_text="A particle (e.g. de, de la, der, van, von)",
                        max_length=16,
                        null=True,
                    ),
                ),
                (
                    "jr",
                    models.CharField(
                        blank=True,
                        help_text="A suffix (e.g. Jr., Sr., III)",
                        max_length=16,
                        null=True,
                    ),
                ),
            ],
            options={
                "ordering": ("last", "first", "von", "jr"),
            },
        ),
        migrations.CreateModel(
            name="AuthorOrder",
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
                    "order",
                    models.IntegerField(
                        help_text="The relative order, with lower numbers (i.e. towards neg. inf.) being first."
                    ),
                ),
                (
                    "author",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="core.author"
                    ),
                ),
                (
                    "bibtex",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="core.bibtex"
                    ),
                ),
            ],
            options={
                "ordering": ("bibtex", "order"),
            },
        ),
    ]