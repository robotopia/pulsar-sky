# Generated by Django 4.2.2 on 2023-06-23 08:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0025_remove_authororder_well_determined_order_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="bibtex",
            name="issue",
            field=models.CharField(blank=True, max_length=64, null=True),
        ),
    ]