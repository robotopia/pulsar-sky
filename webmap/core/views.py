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

def map(request):

    try:
        minJy = float(request.GET.get("minjy"))
    except:
        minJy = 0.001
    minLogJy = np.log10(minJy)

    try:
        maxJy = float(request.GET.get("maxjy"))
    except:
        maxJy = 1
    maxLogJy = np.log10(maxJy)

    try:
        freq = float(request.GET.get("freq"))*1e6 # Get in MHz, convert to Hz
    except:
        freq = 1.4e9
    logFreq = np.log10(freq)
    print(logFreq)

    pulsars = models.Pulsar.objects.filter(spectrum_model__isnull=False)
    context = {
        'data': [{
            'pulsar': pulsar,
            'spectral_fits': models.SpectralFit.objects.filter(pulsar=pulsar, parameter__spectrum_model=pulsar.spectrum_model),
        } for pulsar in pulsars],
        'maxJy': maxJy,
        'maxLogJy': maxLogJy,
        'minJy': minJy,
        'minLogJy': minLogJy,
        'freq_MHz': freq/1e6,
        'logFreq': logFreq,
    }

    return render(request, 'map.html', context)

def pulsar_view(request, pk):

    pulsar = models.Pulsar.objects.get(pk=pk)

    context = {
        "pulsar": pulsar,
    }

    return render(request, 'pulsar.html', context)

def power_law_fit(νnorm, c, α):
    return c*νnorm**α

def power_law(ν, νref, c, α):
    return power_law_fit(ν/νref)

def set_all_atnf_power_laws():

    for pulsar in models.Pulsar.objects.all():
        set_atnf_power_law(pulsar)


def set_atnf_power_law(pulsar, default_spectral_index=-1.6, overwrite=False, set_as_select=True):
    '''
    If overwrite = False, ignore pulsars which already have simple power laws
    '''

    # Ignore pulsars that don't have ATNF flux measurements
    atnf_flux_measurements_queryset = models.ATNFFluxMeasurement.objects.filter(pulsar=pulsar)
    if not atnf_flux_measurements_queryset.exists():
        return False

    # Retrieve the SpectrumModel object corresponding to a simple power law
    simple_power_law = models.SpectrumModel.objects.filter(name="ATNF simple power law").first()
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

    elif len(atnf_flux_measurements) == 2:
        # Calculate the power law explicitly
        X_MHz = np.array([atnf.freq for atnf in atnf_flux_measurements]) # in MHz
        X_ref = np.sqrt(X_MHz[0]*X_MHz[-1]) # in MHz
        X = X_MHz / X_ref # Now normalised to the geometric mean of the range
        Y = np.array([atnf.flux for atnf in atnf_flux_measurements]) # in mJy

        a_value = np.log(Y[1]/Y[0]) / np.log(X[1]/X[0])
        c_value = Y[0] / X[0]**a_value

    else: # if len(...) > 1

        X_MHz = np.array([atnf.freq for atnf in atnf_flux_measurements]) # in MHz
        X_ref = np.sqrt(X_MHz[0]*X_MHz[-1]) # in MHz
        X = X_MHz / X_ref # Now normalised to the geometric mean of the range
        Y = np.array([atnf.flux for atnf in atnf_flux_measurements]) # in mJy

        # Not sure how to handle the case where some flux measurements have errors
        # but others don't. For now, I'll just treat them all as not having errors.
        #sigma = [atnf.error for atnf in atnf_flux_measurements]

        p0 = (0.05, -1.6)
        popt, pcov = curve_fit(power_law_fit, X, Y, p0=p0)

        a_value = popt[1]
        c_value = popt[0]

    # If any of the parameters have turned up non-finite, do nothing with them
    if not np.isfinite(a_value) or not np.isfinite(c_value) or not np.isfinite(X_ref):
        return False

    # ATNF fluxes are in mJy, but pulsar_spectra expects Jy
    c_value /= 1e3

    fit_a = models.SpectralFit.objects.filter(pulsar=pulsar, parameter=a).first()
    if fit_a:
        fit_a.value = a_value
    else:
        fit_a = models.SpectralFit(pulsar=pulsar, parameter=a, value=a_value)
    fit_a.save()

    fit_c = models.SpectralFit.objects.filter(pulsar=pulsar, parameter=c).first()
    if fit_c:
        fit_c.value = c_value
    else:
        fit_c = models.SpectralFit(pulsar=pulsar, parameter=c, value=c_value)
    fit_c.save()

    fit_v0 = models.SpectralFit.objects.filter(pulsar=pulsar, parameter=v0).first()
    if fit_v0:
        fit_v0.value = X_ref*1e6 # in Hz
    else:
        fit_v0 = models.SpectralFit(pulsar=pulsar, parameter=v0, value=X_ref*1e6)
    fit_v0.save()

    if set_as_select:
        if not pulsar.spectrum_model:
            pulsar.spectrum_model = simple_power_law
            pulsar.save()

    return True

def update_atnf_fluxes():

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


def import_atnf():

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

        print(f"Importing {bname}...")

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


def import_spectra():

    cat_dict = collect_catalogue_fluxes()
    pulsars = models.Pulsar.objects.all()
    for pulsar in pulsars:
        print(pulsar)
        try:
            freqs, bands, fluxs, flux_errs, refs = cat_dict[pulsar.jname]
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


def construct_ephemeris(request, pk):

    pulsar = models.Pulsar.objects.get(pk=pk)
    if not pulsar:
        return HttpResponseBadRequest(f"Pulsar ID {pk} not found")

    measurements = models.PulsarPropertyMeasurement.objects.filter(pulsar=pulsar, pulsar_property__ephemeris_parameter_name__isnull=False)
    if not measurements.exists():
        return HttpResponseBadRequest(f"{pulsar} does not have any measurements")

    context = {
        'pulsar': pulsar,
        'measurements': measurements,
    }

    return render(request, 'construct_ephemeris.html', context)


def init_spectrum_models():

    spl = models.SpectrumModel.objects.create(name="Simple power law", pulsar_spectra_name="simple_power_law")
    aspl = models.SpectrumModel.objects.create(name="ATNF simple power law", pulsar_spectra_name="simple_power_law")
    bpl = models.SpectrumModel.objects.create(name="Broken power law", pulsar_spectra_name="broken_power_law")
    dto = models.SpectrumModel.objects.create(name="Double turn-over", pulsar_spectra_name="double_turn_over_spectrum")
    hfco = models.SpectrumModel.objects.create(name="High frequency cut-off power law", pulsar_spectra_name="high_frequency_cut_off_power_law")
    lp = models.SpectrumModel.objects.create(name="Log-parabolic", pulsar_spectra_name="log_parabolic_spectrum")
    lfto = models.SpectrumModel.objects.create(name="Low frequency turn-over power law", pulsar_spectra_name="low_frequency_turn_over_power_law")

    bpl.parameters.create(name='vb')
    bpl.parameters.create(name='a1')
    bpl.parameters.create(name='a2')
    bpl.parameters.create(name='c')
    bpl.parameters.create(name='v0')

    dto.parameters.create(name='vc')
    dto.parameters.create(name='vpeak')
    dto.parameters.create(name='a')
    dto.parameters.create(name='beta')
    dto.parameters.create(name='c')
    dto.parameters.create(name='v0')

    hfco.parameters.create(name='vc')
    hfco.parameters.create(name='a')
    hfco.parameters.create(name='c')
    hfco.parameters.create(name='v0')

    lp.parameters.create(name='a')
    lp.parameters.create(name='b')
    lp.parameters.create(name='c')
    lp.parameters.create(name='v0')

    lfto.parameters.create(name='vpeak')
    lfto.parameters.create(name='a')
    lfto.parameters.create(name='c')
    lfto.parameters.create(name='beta')
    lfto.parameters.create(name='v0')

    spl.parameters.create(name='a')
    spl.parameters.create(name='c')
    spl.parameters.create(name='v0')

    aspl.parameters.create(name='a')
    aspl.parameters.create(name='c')
    aspl.parameters.create(name='v0')

