# Generated by Django 4.2.2 on 2023-07-04 09:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0034_pulsarpropertymeasurement_notes'),
    ]

    operations = [
        migrations.AddField(
            model_name='pulsarproperty',
            name='ephemeris_parameter_name',
            field=models.CharField(blank=True, help_text='The name of the equivalent parameter in psrcat-style ephemeris files.', max_length=64, null=True),
        ),
    ]
