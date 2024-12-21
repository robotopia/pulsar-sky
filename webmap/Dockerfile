FROM python:3.11

# Copy webapp into container
RUN mkdir /pulsar-sky
WORKDIR /pulsar-sky
COPY . /pulsar-sky/

# Install necessary packages
RUN apt-get update
RUN apt-get install build-essential default-libmysqlclient-dev python3.11-dev python3-pip gosu locales vim bash -yqq

# Install psrcat
RUN wget -O psrcat_pkg.tar.gz https://www.atnf.csiro.au/research/pulsar/psrcat/downloads/psrcat_pkg.tar.gz
RUN tar xvzf psrcat_pkg.tar.gz
WORKDIR psrcat_tar
RUN sed -i -n '/rm/!p' makeit
RUN sed -i 's/gcc/gcc -fcommon/' makeit
RUN bash -c "source makeit"
ENV PSRCAT_RUNDIR=/pulsar-sky/psrcat_tar \
    PSRCAT_FILE=/pulsar-sky/psrcat_tar/psrcat.db

WORKDIR /pulsar-sky

# Install Python requirements
RUN pip3 install uwsgi
RUN pip3 install -r requirements.txt

# Start the container with entrypoint script
ENTRYPOINT ["/pulsar-sky/entrypoint.sh"]

