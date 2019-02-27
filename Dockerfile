FROM python:3.7 as builder

LABEL maintainer="Kacper Skowronski <k.skowronski1993@gmail.com>"

######################
# Set Application Environment Variables
######################

ENV PYTHONUNBUFFERED=1


######################
# Install Dependencies
######################
COPY /requirements.txt /req/
RUN pip3 install -U pip
RUN cd /req && pip3 install -r requirements.txt

COPY . /webapps

EXPOSE 8000
WORKDIR /webapps
