# Build: docker build -t convert -f convert.Dockerfile .
# Run: docker run --name convertapp convert:local
FROM ubuntu:22.04

ENV DEBIAN_FRONTEND noninteractive

# Install Python
RUN apt-get update && apt-get -y upgrade && \
    apt-get -y install python3 && \
    apt update && apt install python3-pip -y && \
    apt-get install -y bash default-jre default-jdk

# Install LibreOffice
RUN  apt-get --no-install-recommends install libreoffice -y
RUN  apt-get install -y libreoffice-java-common

# Create app directory 
RUN mkdir -p /app
RUN mkdir -p /app/pdf

# Copy the current directory contents into the container at /app
COPY . /app
WORKDIR /app

# Execute the conversion script
RUN chmod +x convert.sh
RUN sh convert.sh
