#!/bin/bash
set -e

# This is only run on the first start-up of the container.
CONTAINER_FIRST_STARTUP="CONTAINER_FIRST_STARTUP"
if [ ! -e /$CONTAINER_FIRST_STARTUP ]; then
    touch /$CONTAINER_FIRST_STARTUP
fi

if [ "$DJANGO_DEBUG" == "True" ]
then
    # This runs the web app locally through Django
    python3 manage.py runserver 0.0.0.0:8000
else
    # This runs the webapp using uwsgi and creates a socket that nginx uses
    uwsgi --ini /pulsar-sky/pulsar-sky.uwsgi.ini
fi
