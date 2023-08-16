# Build: docker build -t convert:local -f convert/convert.Dockerfile .
# Run: docker run --name convertapp convert:local
FROM python:3.9-slim-bullseye

ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update && \
    apt-get -y upgrade && \
    apt-get -y install python3 python3-pip bash default-jre default-jdk libreoffice libreoffice-java-common pv && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN pip3 install --upgrade pip
RUN pip3 install tqdm

# Create app directory 
RUN mkdir -p /app
WORKDIR /app

COPY convert_2/* /app/

# Add execution permission to conversion script
RUN chmod +x convert.sh

# Create command to run on container start
CMD ["/bin/bash", "convert.sh"]
