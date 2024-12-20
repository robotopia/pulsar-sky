from django.db import models
from django.db.models import Q
from django.utils.html import format_html

from django.core.exceptions import ValidationError

import literature.models as literature_models

from astropy.coordinates import SkyCoord
import astropy.units as u

# Create your models here.

class ATNFFluxMeasurement(models.Model):

    pulsar = models.ForeignKey(
        "Pulsar",
        on_delete=models.CASCADE,
        related_name="atnf_flux_measurements",
    )

    freq = models.FloatField(
        help_text="The frequency in MHz",
    )

    flux = models.FloatField(
        help_text="The flux density in mJy",
    )

    error = models.FloatField(
        null=True,
        blank=True,
        help_text="The error on the flux density in mJy",
    )

    def flux_str(self):
        if self.error is not None:
            return f"{self.flux} ± {self.error} mJy"
        else:
            return f"{self.flux} mJy"

    def __str__(self):
        return f"{self.pulsar}: S{self.freq} = "#{self.flux_str}"

    class Meta:
        verbose_name = "ATNF flux measurement set"
        verbose_name_plural = "ATNF flux measurement sets"
        ordering = ("pulsar", "freq",)
        constraints = [
            models.UniqueConstraint(
                fields=["pulsar", "freq"],
                name='unique_pulsar_freq',
            ),
        ]


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

    pdot = models.FloatField(
        verbose_name="Period derivative (s/s)",
        blank=True,
        null=True,
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
    def DM(self):
        if self.dm is not None and self.dm_error is not None:
            return f"{self.dm} ± {self.dm_error}"
        if self.dm is not None:
            return f"{self.dm}"
        return None

    DM.fget.short_description = "DM (pc/cm³)"

    @property
    def RM(self):
        if self.rm is not None and self.rm_error is not None:
            return f"{self.rm} ± {self.rm_error}"
        if self.rm is not None:
            return f"{self.rm}"
        return None

    RM.fget.short_description = "RM (rad/m²)"

    @property
    def ra_dec(self):
        if self.ra and self.dec:
            coord = SkyCoord(ra=self.ra*u.deg, dec=self.dec*u.deg)
            return coord.to_string('hmsdms', precision=1)

    ra_dec.fget.short_description = "Coordinates (RA Dec)"

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
        help_text="The name used to identify the functional form (as implemented in pulsar_sectra).",
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
        return f"{self.spectrum_model}: {self.name}"

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


class PulsarProperty(models.Model):

    name = models.CharField(
        max_length=64,
        unique=True,
    )

    symbol = models.CharField(
        max_length=16,
        null=True,
        blank=True,
    )

    ephemeris_parameter_name = models.CharField(
        max_length=64,
        null=True,
        blank=True,
        help_text="The name of the equivalent parameter in psrcat-style ephemeris files.",
    )

    unit = models.CharField(
        null=True,
        blank=True,
        max_length=64,
        help_text="A string that can be parsed by astropy.units. Leave blank if dimensionless.",
    )

    description = models.TextField(
        blank=True,
        null=True,
    )

    def clean(self):

        if self.unit:
            try:
                unit = u.Unit(self.unit)
            except:
                raise ValidationError(f'Unable to interpret {self.unit} as a valid Astropy unit')

    def __str__(self):
        if self.symbol:
            return f"{self.symbol}, {self.name}"

        return self.name

    class Meta:
        verbose_name_plural = "Pulsar properties"
        ordering = ("symbol", "name",)


class PulsarPropertyMeasurement(models.Model):

    pulsar = models.ForeignKey(
        "Pulsar",
        on_delete=models.CASCADE,
    )

    pulsar_property = models.ForeignKey(
        "PulsarProperty",
        on_delete=models.CASCADE,
    )

    value = models.CharField(
        max_length=1024,
    )

    error = models.CharField(
        null=True,
        blank=True,
        max_length=1024,
        help_text="The error on \"value\". If error_low is given, then this value should be interpreted as the upper error.",
    )

    error_low = models.CharField(
        null=True,
        blank=True,
        max_length=1024,
        help_text="The lower error on \"value\". This should only be used if the error field is non-empty.",
    )

    is_lower_limit = models.BooleanField(
        default=False,
        verbose_name="Lower limit?",
    )

    is_upper_limit = models.BooleanField(
        default=False,
        verbose_name="Upper limit?",
    )

    mode = models.CharField(
        null=True,
        blank=True,
        max_length=16,
        help_text="The mode, if any, to which this measurement applies.",
    )

    unit = models.CharField(
        null=True,
        blank=True,
        max_length=64,
        help_text="A string that can be parsed by astropy.units. Leave blank if dimensionless. Must be equivalent to the parent property's unit.",
    )

    freq_MHz = models.FloatField(
        verbose_name="Frequency (MHz)",
        null=True,
        blank=True,
        help_text="The (centre) frequency at which this measurement was made.",
    )

    bandwidth_MHz = models.FloatField(
        verbose_name="Bandwidth (MHz)",
        null=True,
        blank=True,
        help_text="The frequency bandwidth with which this measurement was made.",
    )

    mjd = models.FloatField(
        null=True,
        blank=True,
        help_text="The MJD when the measurement was made.",
    )

    time_span_s = models.FloatField(
        verbose_name="Time span (s)",
        null=True,
        blank=True,
        help_text="The time span of the data used to make this measurement.",
    )

    bibtex = models.ForeignKey(
        literature_models.Bibtex,
        on_delete=models.CASCADE,
    )

    notes = models.TextField(
        null=True,
        blank=True,
        help_text="Any extra notes about this measurement.",
    )

    @property
    def value_display(self):
        valstr = f"{self.value}"

        if self.error and self.error_low:
            valstr += f" (+{self.error} / -{self.error_low})"
        elif self.error:
            valstr += f" ± {self.error}"

        if self.unit:
            valstr += f" {u.Unit(self.unit)}"

        if self.is_lower_limit:
            valstr = "≥ " + valstr
        elif self.is_upper_limit:
            valstr = "≤ " + valstr

        return valstr

    def clean(self):

        if self.unit:
            try:
                u1 = u.Unit(self.unit)
            except:
                raise ValidationError(f'Unable to interpret {self.unit} as a valid Astropy unit')

            u2 = u.Unit(self.pulsar_property.unit)
            if not u1.is_equivalent(u2):
                raise ValidationError(f'The unit "{self.unit}" must be dimensionally equivalent to {self.pulsar_property.unit}')

    def __str__(self):
        return f"{self.pulsar_property} of {self.pulsar} ({self.bibtex})"

    class Meta:
        ordering = ("pulsar", "pulsar_property", "bibtex__year",)


class PulsarMention(models.Model):

    IMPORTANCE_1 = '1'
    IMPORTANCE_2 = '2'
    IMPORTANCE_3 = '3'

    IMPORTANCE_CHOICES = [
        (IMPORTANCE_1, 'Incidental mention'),
        (IMPORTANCE_2, 'Frequent mention'),
        (IMPORTANCE_3, 'Central object of study'),
    ]

    pulsar = models.ForeignKey(
        "Pulsar",
        on_delete=models.PROTECT,
        help_text="The pulsar mentioned in the reference.",
    )

    bibtex = models.ForeignKey(
        literature_models.Bibtex,
        on_delete=models.PROTECT,
        help_text="The reference which mentions the pulsar.",
    )

    importance = models.CharField(
        max_length=1,
        null=True,
        blank=True,
        choices=IMPORTANCE_CHOICES,
    )

    def __str__(self):
        return f"{self.pulsar} in {self.bibtex}"

    class Meta:
        ordering = ("pulsar", "bibtex",)
        constraints = [
            models.UniqueConstraint(
                fields=['pulsar', 'bibtex'],
                name='unique_pulsar_mention',
            ),
        ]

