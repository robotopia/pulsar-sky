# Generated by Django 4.1.4 on 2023-06-11 10:27

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Pulsar",
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
                    "bname",
                    models.CharField(
                        blank=True,
                        help_text='The "B"-name (without the preceding "B")',
                        max_length=16,
                        null=True,
                    ),
                ),
                (
                    "jname",
                    models.CharField(
                        blank=True,
                        help_text='The "J"-name (without the preceding "J")',
                        max_length=16,
                        null=True,
                    ),
                ),
                (
                    "ra",
                    models.FloatField(
                        blank=True, null=True, verbose_name="Right ascension (deg)"
                    ),
                ),
                (
                    "dec",
                    models.FloatField(
                        blank=True, null=True, verbose_name="Declination (deg)"
                    ),
                ),
                (
                    "period",
                    models.FloatField(
                        blank=True, help_text="The rotation period (s).", null=True
                    ),
                ),
                (
                    "dm",
                    models.FloatField(
                        blank=True, null=True, verbose_name="DM (pc/cm³)"
                    ),
                ),
                (
                    "dm_error",
                    models.FloatField(
                        blank=True, null=True, verbose_name="± DM error (pc/cm³)"
                    ),
                ),
                (
                    "rm",
                    models.FloatField(
                        blank=True, null=True, verbose_name="RM (rad/m²)"
                    ),
                ),
                (
                    "rm_error",
                    models.FloatField(
                        blank=True, null=True, verbose_name="± RM error (rad/m²)"
                    ),
                ),
            ],
            options={
                "ordering": ("ra", "dec"),
            },
        ),
        migrations.AddConstraint(
            model_name="pulsar",
            constraint=models.CheckConstraint(
                check=models.Q(
                    ("bname__isnull", False), ("jname__isnull", False), _connector="OR"
                ),
                name="name_supplied",
            ),
        ),
    ]
