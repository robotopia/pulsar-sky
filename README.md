# pulsar-sky
A Django-based webapp to make an interactive map of pulsars in the radio sky

## Installation and setup

### psrcat

Follow the instructions at [the ATNF Pulsar Catalogue page](https://www.atnf.csiro.au/people/pulsar/psrcat/download.html).
Note that you will need catalogue >= v1.70.

### Django

#### Install (Python) dependencies

You may like to use a Python virtual environment

In the `webmap` directory, run

```
pip install -r requirements.txt
```

#### Create a Django superuser

In the `webmap` directory, run

```
python manage.py createsuperuser
```

...and follow the prompts.

#### Run the server

In the `webmap` directory, run

```
python manage.py runserver [port]
```
where `[port]` can be any available port.
If none is provided, the default is 8000.

## Usage

When running, the server can be accessed in a browser with the URL `http://localhost:8000/` (or whichever port you chose during setup).
However, going to that URL alone will result in a 404 not found, as only a limited number of paths are implemented, and `/` is not one of them.
The following paths are available, which you append to the URL given above (e.g. `http://localhost:8000/admin`).
When you go to these paths, the action described in the table is performed, and then you are redirected to the admin site.
The exceptions to this behaviour are `admin` itself, which is the standard Django site, and `core/map`, which is the interactive map.

| Path | Description |
| ---- | ----------- |
| `admin` | The standard Django admin interface |
| `core/import_atnf` | Imports the pulsars from the ATNF catalogue |
| `core/update_atnf_fluxes` | Imports the flux density data from the ATNF catalogue for the pulsars that have already been imported |
| `core/import_spectra` | Imports the spectral fits (not the flux densities) from [pulsar_spectra](https://github.com/NickSwainston/pulsar_spectra) |
| `core/set_all_atnf_power_laws` | Fits power laws to ATNF pulsar data (for pulsars that don't already have spectral fits) |
| `core/map` | The interactive map showing the relative brightness of pulsars in the sky |

Some of the above functions are also accessible via Django admin "actions".

## Screenshot of pulsar sky map

![screenshot.png](screenshot.png)
