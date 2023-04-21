#!/usr/bin/sh
docker build -t convert:local -f convert.Dockerfile .
docker run --name convertapp convert:local
docker cp convertapp:app/pdf ../pdf
docker rm convertapp
docker rmi convert:local