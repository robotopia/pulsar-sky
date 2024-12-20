FROM python:3.11

# Copy webapp into container
RUN mkdir /pulsar-sky
WORKDIR /pulsar-sky
COPY . /pulsar-sky/

# Install necessary packages
RUN apt-get update
RUN apt-get install build-essential default-libmysqlclient-dev mysql-server mysql-client python3.11-dev python3-pip gosu locales vim -yqq

# Install Python requirements
RUN pip3 install uwsgi
RUN pip3 install -r requirements.txt

# Start the container with entrypoint script
ENTRYPOINT ["/pulsar-sky/entrypoint.sh"]

