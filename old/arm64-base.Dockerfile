FROM ubuntu:22.04

ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update && apt-get -y upgrade && \
    apt-get -y install python3 && \
    apt-get -y install python3-venv && \
    apt-get -y install python3-tk && \
    apt update && apt install python3-pip -y && \
    apt-get install -y bash make ghostscript && \
    apt-get install -y default-jre default-jdk

# Installing LibreOffice and java
RUN  apt-get --no-install-recommends install libreoffice -y
RUN  apt-get install -y libreoffice-java-common

ARG CACHEBUST=1

# Create the application directory
RUN mkdir -p /app

# Copy the application code and files to scrape
COPY control /app/control

# Set WD
WORKDIR /app/control

# Install dependencies
RUN make setup 
RUN chmod +x run.sh