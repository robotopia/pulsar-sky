# Generated by Django 4.2.2 on 2023-06-24 01:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0026_bibtex_issue"),
    ]

    operations = [
        migrations.AddField(
            model_name="pulsarpropertymeasurement",
            name="error_low",
            field=models.CharField(
                blank=True,
                help_text='The lower error on "value". This should only be used if the error field is non-empty.',
                max_length=1024,
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="pulsarpropertymeasurement",
            name="error",
            field=models.CharField(
                blank=True,
                help_text='The error on "value". If error_low is given, then this value should be interpreted as the upper error.',
                max_length=1024,
                null=True,
            ),
        ),
    ]