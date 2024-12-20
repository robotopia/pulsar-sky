# Generated by Django 4.2.2 on 2023-07-04 07:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0032_pulsarproperty_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='pulsarpropertymeasurement',
            name='is_lower_limit',
            field=models.BooleanField(default=False, verbose_name='Lower limit?'),
        ),
        migrations.AddField(
            model_name='pulsarpropertymeasurement',
            name='is_upper_limit',
            field=models.BooleanField(default=False, verbose_name='Upper limit?'),
        ),
    ]
