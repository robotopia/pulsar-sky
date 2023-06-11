from django.db import models
from django.db.models import Q

from django.core.exceptions import ValidationError

# Create your models here.

class Pulsar(models.Model):

    bname = models.CharField(
        max_length=16,
        null=True,
        blank=True,
    )

    jname = models.CharField(
        max_length=16,
        null=True,
        blank=True,
    )

    ra = models.FloatField(
        blank=True,
        null=True,
        verbose_name="Right ascension (deg)",
    )

    dec = models.FloatField(
        blank=True,
        null=True,
        verbose_name="Declination (deg)",
    )

    period = models.FloatField(
        blank=True,
        null=True,
        help_text="The rotation period (s).",
    )

    dm = models.FloatField(
        verbose_name="DM (pc/cm³)",
        blank=True,
        null=True,
    )

    dm_error = models.FloatField(
        verbose_name="± DM error (pc/cm³)",
        blank=True,
        null=True,
    )

    rm = models.FloatField(
        verbose_name="RM (rad/m²)",
        blank=True,
        null=True,
    )

    rm_error = models.FloatField(
        verbose_name="± RM error (rad/m²)",
        blank=True,
        null=True,
    )

    catalogue_version = models.CharField(
        max_length=64,
        blank=True,
        null=True,
    )

    spectrum_model = models.ForeignKey(
        "SpectrumModel",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )

    @property
    def name(self):
        if self.bname:
            return f"{self.bname}"
        elif self.jname:
            return f"{self.jname}"
        else:
            # Should never get here, due to constraint that either bname or
            # jname must be supplied
            raise Exception("Either JNAME or BNAME must be supplied.")

    def __str__(self):
        return self.name

    class Meta:
        ordering = ("ra", "dec",)
        constraints = [
            models.CheckConstraint(
                check=Q(bname__isnull=False) | Q(jname__isnull=False),
                name="name_supplied",
            ),
            models.UniqueConstraint(
                fields=['bname', 'jname'],
                name='unique_names',
            ),
        ]


class SpectrumModel(models.Model):

    name = models.CharField(
        max_length=128,
    )

    pulsar_spectra_name = models.CharField(
        max_length=128,
        unique=True,
    )

    def __str__(self):
        return self.name

    class Meta:
        ordering = ("name",)


class SpectrumModelParameter(models.Model):

    spectrum_model = models.ForeignKey(
        "SpectrumModel",
        on_delete=models.CASCADE,
        related_name="parameters",
    )

    name = models.CharField(
        max_length=16,
    )

    def __str__(self):
        return self.name

    class Meta:
        ordering = ("spectrum_model", "name",)
        unique_together = [["spectrum_model", "name"]]


class SpectralFit(models.Model):

    pulsar = models.ForeignKey(
        "Pulsar",
        on_delete=models.CASCADE,
        related_name="fits",
    )

    parameter = models.ForeignKey(
        "SpectrumModelParameter",
        on_delete=models.CASCADE,
        related_name="fits",
    )

    value = models.FloatField()

    def __str__(self):
        return f"{self.pulsar}: {self.parameter} = {self.value}"

    class Meta:
        ordering = ("pulsar", "parameter",)
        unique_together = [["pulsar", "parameter"]]
