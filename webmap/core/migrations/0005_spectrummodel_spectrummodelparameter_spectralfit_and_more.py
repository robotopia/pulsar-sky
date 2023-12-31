# Generated by Django 4.2.2 on 2023-06-11 12:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0004_alter_pulsar_bname_alter_pulsar_jname"),
    ]

    operations = [
        migrations.CreateModel(
            name="SpectrumModel",
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
                ("name", models.CharField(max_length=128)),
            ],
            options={
                "ordering": ("name",),
            },
        ),
        migrations.CreateModel(
            name="SpectrumModelParameter",
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
                ("name", models.CharField(max_length=16)),
                (
                    "spectral_model",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="parameters",
                        to="core.spectrummodel",
                    ),
                ),
            ],
            options={
                "ordering": ("spectral_model", "name"),
            },
        ),
        migrations.CreateModel(
            name="SpectralFit",
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
                ("value", models.FloatField()),
                (
                    "parameter",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="fits",
                        to="core.spectrummodelparameter",
                    ),
                ),
                (
                    "pulsar",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="fits",
                        to="core.pulsar",
                    ),
                ),
            ],
            options={
                "ordering": ("pulsar", "parameter"),
            },
        ),
        migrations.AddField(
            model_name="pulsar",
            name="spectrum_model",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="core.spectrummodel",
            ),
        ),
    ]
