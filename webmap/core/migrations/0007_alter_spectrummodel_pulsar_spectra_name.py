# Generated by Django 4.2.2 on 2023-06-11 13:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0006_spectrummodel_pulsar_spectra_name"),
    ]

    operations = [
        migrations.AlterField(
            model_name="spectrummodel",
            name="pulsar_spectra_name",
            field=models.CharField(default="asdf", max_length=128),
            preserve_default=False,
        ),
    ]
