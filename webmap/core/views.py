from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseRedirect

from . import models
from django.db.models import Q

import subprocess

from pulsar_spectra.catalogue import collect_catalogue_fluxes
from pulsar_spectra.spectral_fit import find_best_spectral_fit

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

    #return redirect(reverse('admin:core_spectralfit_changelist'))
    return HttpResponse("ok", headers={"Content-Type": "text/plain"})
