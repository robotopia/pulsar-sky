from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseRedirect

from . import models
from django.db.models import Q

import subprocess
from scipy.optimize import curve_fit
import numpy as np

from pulsar_spectra.catalogue import collect_catalogue_fluxes
from pulsar_spectra.spectral_fit import find_best_spectral_fit

def power_law_fit(νnorm, c, α):
    return c*νnorm**α

def power_law(ν, νref, c, α):
    return power_law_fit(ν/νref)

def set_atnf_power_law(pulsar, default_spectral_index=-1.6, overwrite=False):
    '''
    If overwrite = False, ignore pulsars which already have simple power laws
    '''

    # Ignore pulsars that don't have ATNF flux measurements
    atnf_flux_measurements_queryset = models.ATNFFluxMeasurement.objects.filter(pulsar=pulsar)
    if not atnf_flux_measurements_queryset.exists():
        return False

    # Retrieve the SpectrumModel object corresponding to a simple power law
    simple_power_law = models.SpectrumModel.objects.filter(name="Simple power law").first()
    if not simple_power_law:
        # ...then we have bigger problems. Abort! Abort!
        return False

    # Retrieve the three simple power law model parameters
    a = models.SpectrumModelParameter.objects.filter(spectrum_model=simple_power_law, name="a").first()
    c = models.SpectrumModelParameter.objects.filter(spectrum_model=simple_power_law, name="c").first()
    v0 = models.SpectrumModelParameter.objects.filter(spectrum_model=simple_power_law, name="v0").first()

    if not a or not c or not v0:
        # ...then we have bigger problems. Abort! Abort!
        return False

    # If overwrite = False, ignore pulsars which already have simple power laws
    spectral_fit = models.SpectralFit.objects.filter(pulsar=pulsar, parameter__spectrum_model=simple_power_law).all()
    if spectral_fit.exists() and overwrite == False:
        return False

    # If we got this far, we're definitely going to be adding/overwriting this pulsar's power law fit
    print(f"Updating {pulsar}'s {simple_power_law}...")

    # That means we've got to DO the fit on the ATNF data...
    atnf_flux_measurements = atnf_flux_measurements_queryset.all()

    # If there is only one measurement, assume a spectral index
    if len(atnf_flux_measurements) == 1:

        atnf = atnf_flux_measurements.first()
        X_ref = atnf.freq # in MHz
        a_value = default_spectral_index
        c_value = atnf.flux

    else: # if len(...) > 1

        X_MHz = np.array([atnf.freq for atnf in atnf_flux_measurements]) # in MHz
        X_ref = np.sqrt(X_MHz[0]*X_MHz[-1]) # in MHz
        X = X_MHz / X_ref # Now normalised to the geometric mean of the range
        Y = np.array([atnf.flux for atnf in atnf_flux_measurements]) # in mJy

        # Not sure how to handle the case where some flux measurements have errors
        # but others don't. For now, I'll just treat them all as not having errors.
        #sigma = [atnf.error for atnf in atnf_flux_measurements]

        popt, pcov = curve_fit(power_law_fit, X, Y)

        a_value = popt[1]
        c_value = popt[0]

    fit_a = models.SpectralFit.objects.filter(pulsar=pulsar, parameter=a).first()
    if fit_a:
        fit_a.value = a_value
    else:
        fit_a = models.SpectralFit(pulsar=pulsar, parameter=a, value=a_value)

    fit_c = models.SpectralFit.objects.filter(pulsar=pulsar, parameter=c).first()
    if fit_c:
        fit_c.value = c_value
    else:
        fit_c = models.SpectralFit(pulsar=pulsar, parameter=c, value=c_value)

    fit_v0 = models.SpectralFit.objects.filter(pulsar=pulsar, parameter=v0).first()
    if fit_v0:
        fit_v0.value = X_ref*1e6 # in Hz
    else:
        fit_v0 = models.SpectralFit(pulsar=pulsar, parameter=c, value=X_ref*1e6)

    return True

def update_atnf_fluxes(request):

    # Now grab the catalogue's contents
    completed_process = subprocess.run(
        ['psrcat', '-nonumber', '-nohead', '-o', 'short_error', '-c',
         'bname jname S30 S40 S50 S60 S80 S100 S150 S200 S300 S350 S400 S600 S700 S800 S900 S1400 S1600 S2000 S3000 S4000 S5000 S6000 S8000 S10G S20G S50G S100G S150G'],
        capture_output=True,
    )
    stdout = completed_process.stdout.decode("utf-8")

    # ***WARNING***
    # The below column indices may change for different versions of the catalogue!!
    freqs = [30, 40, 50, 60, 80, 100, 150, 200, 300, 350, 400, 600, 700, 800, 900, 1400, 1600, 2000, 3000, 4000, 5000, 6000, 8000, 10000, 20000, 50000, 100000, 150000]
    flux_cols = [2, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25, 27, 29, 31, 33, 35, 37, 39, 41, 43, 45, 47, 48, 49, 50, 52]
    error_cols = [None, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32, 34, 36, 38, 40, 42, 44, 46, None, None, None, 51, 53]

    for line in stdout.split('\n'):

        tokens = line.split()

        # Ignore problematic lines with too few tokens
        if len(tokens) < 12:
            continue

        bname = None if tokens[0] == '*' else tokens[0]
        jname = None if tokens[1] == '*' else tokens[1]

        # Find the matching pulsar, otherwise ignore
        pulsar = models.Pulsar.objects.filter(bname=bname, jname=jname).first()
        if not pulsar:
            continue

        for i in range(len(freqs)):
            freq = freqs[i]
            try:
                flux = float(tokens[flux_cols[i]])
            except:
                # If there's no flux for this frequency, skip this and go to the next frequency
                continue
            try:
                error = float(tokens[error_cols[i]])
            except:
                # If there's no error, just set it to None
                error = None

            # Look for matching entries
            atnf_flux_measurement = models.ATNFFluxMeasurement.objects.filter(pulsar=pulsar, freq=freq).first()

            if atnf_flux_measurement is not None:
                # Update the existing entry
                atnf_flux_measurement.flux = flux
                atnf_flux_measurement.error = error
                print(f"Updating {atnf_flux_measurement}...")
            else:
                # Make a new entry
                atnf_flux_measurement = models.ATNFFluxMeasurement(
                    pulsar=pulsar,
                    freq=freq,
                    flux=flux,
                    error=error,
                )
                print(f"Creating {atnf_flux_measurement}...")

            atnf_flux_measurement.save()

    #return HttpResponse("ok", headers={"Content-Type": "text/plain"})
    return redirect(reverse('admin:core_atnffluxmeasurement_changelist'))

def import_atnf(request):

    # Grab the ATNF catalogue number (this also tests whether psrcat is installed)
    completed_process = subprocess.run(
        ['psrcat', '-v'],
        capture_output=True,
    )
    stdout = completed_process.stdout.decode("utf-8")
    catalogue_version = stdout.split()[-1]

    # Now grab the catalogue's contents
    completed_process = subprocess.run(
        ['psrcat', '-nonumber', '-nohead', '-o', 'short_error', '-c', 'bname jname rajd decjd p0 dm rm'],
        capture_output=True,
    )
    stdout = completed_process.stdout.decode("utf-8")

    atnf_pulsars = []
    bnames = []
    jnames = []

    for line in stdout.split('\n'):

        tokens = line.split()

        # Ignore problematic lines with too few tokens
        if len(tokens) < 12:
            continue

        bname = None if tokens[0] == '*' else tokens[0]
        jname = None if tokens[1] == '*' else tokens[1]

        try:
            ra = float(tokens[2])
        except:
            ra = None
        try:
            dec = float(tokens[4])
        except:
            dec = None
        try:
            period = float(tokens[6])
        except:
            period = None
        try:
            dm = float(tokens[8])
        except:
            dm = None
        try:
            dm_error = float(tokens[9])
        except:
            dm_error = None
        try:
            rm = float(tokens[10])
        except:
            rm = None
        try:
            rm_error = float(tokens[11])
        except:
            rm_error = None

        atnf_pulsars.append(
            models.Pulsar(
                bname=bname,
                jname=jname,
                ra=ra,
                dec=dec,
                period=period,
                dm=dm,
                dm_error=dm_error,
                rm=rm,
                rm_error=rm_error,
                catalogue_version=catalogue_version,
            )
        )

        bnames.append(bname)
        jnames.append(jname)

    duplicates = models.Pulsar.objects.filter(Q(bname__in=bnames) | Q(jname__in=jnames))
    duplicate_names = [p.name for p in duplicates]
    new_pulsars = [p for p in atnf_pulsars if p.name not in duplicate_names]
    models.Pulsar.objects.bulk_create(new_pulsars)

    return redirect(reverse('admin:core_pulsar_changelist'))

def import_spectra(request):

    cat_dict = collect_catalogue_fluxes()
    pulsars = models.Pulsar.objects.all()
    for pulsar in pulsars:
        print(pulsar)
        try:
            freqs, bands, fluxs, flux_errs, refs = cat_dict[pulsar.name]
            best_model_name, iminuit_result, fit_info, p_best, p_category = find_best_spectral_fit(
                pulsar.name,
                freqs,
                bands,
                fluxs,
                flux_errs,
                refs,
                plot_best=False
            )

        except:
            continue

        # Find the django counterpart of the spectrum model
        spectrum_model = models.SpectrumModel.objects.filter(pulsar_spectra_name=best_model_name).first()
        if not spectrum_model:
            print(f"Couldn't find SpectrumModel {best_model_name}")
            continue
        pulsar.spectrum_model = spectrum_model
        pulsar.save()
        for p, v, _ in zip(iminuit_result.parameters, iminuit_result.values, iminuit_result.errors):
            fit = models.SpectralFit.objects.filter(pulsar=pulsar, parameter__name=p).first()
            if fit:
                # Update the value
                fit.value=v
            else:
                # Find a matching parameter object, or create a new one
                parameter = models.SpectrumModelParameter.objects.filter(
                    spectrum_model=spectrum_model,
                    name=p,
                ).first()

                if not parameter:
                    # Create a new parameter
                    parameter = models.SpectrumModelParameter(
                        spectrum_model=spectrum_model,
                        name=p,
                    )
                    parameter.save()

                # And a new fit
                fit = models.SpectralFit(pulsar=pulsar, parameter=parameter, value=v)
                fit.save()

    return redirect(reverse('admin:core_spectralfit_changelist'))
    #return HttpResponse("ok", headers={"Content-Type": "text/plain"})
