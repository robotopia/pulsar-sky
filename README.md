# pulsar-sky
A Django-based webapp to make an interactive map of pulsars in the radio sky

## Installation and setup

### psrcat

Follow the instructions at [the ATNF Pulsar Catalogue page](https://www.atnf.csiro.au/people/pulsar/psrcat/download.html).

> [!info]
> You will need catalogue >= v1.70. This has been tested up to v2.5.1.

### Django

#### Install (Python) dependencies

You may like to use a Python virtual environment.

In the `webmap` directory, run

```
pip install -r requirements.txt
```

#### Initialise (MySQL/Mariadb) database

Create an empty MySQL/Mariadb database called `pulsar_sky`:
```
Mariadb> CREATE DATABASE pulsar_sky;
```

Create the schema using Django's `migrate` utility.
```
python manage.py migrate
```

#### Create a Django superuser

In the `webmap` directory, run

```
python manage.py createsuperuser
```

...and follow the prompts.

#### Populate the database

Some helper functions have been created to import data from `psrcat` and `pulsar_spectra` when setting up for the first time. These functions can be called from the Django-provided shell environment:

```
python manage.py shell
>>> from core import views
>>> views.import_atnf()             # Imports the pulsars from the ATNF catalogue
>>> views.update_atnf_fluxes()      # Imports the flux density data from the ATNF catalogue for the pulsars that have already been imported
>>> views.import_spectra()          # Imports the spectral fits (not the flux densities) from pulsar_spectra
>>> views.set_all_atnf_power_laws() # Fits power laws to ATNF pulsar data (for pulsars that don't already have spectral fits)
```

#### Run the server

In the `webmap` directory, run

```
python manage.py runserver [port]
```
where `[port]` can be any available port.
If none is provided, the default is 8000.

## Screenshot of pulsar sky map

`core/map`:

![screenshot.png](screenshot.png)
