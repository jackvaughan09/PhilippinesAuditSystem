#!/bin/bash
#creates these folders if they don't exist just in case.
if [ ! -d "data/pdf" ]; then
  mkdir -p "data/pdf"
fi
if [ ! -d "data/zip" ]; then
  mkdir -p "data/zip"
fi
if [ ! -d "data/xlsx" ]; then
  mkdir -p "data/xlsx"
fi
if [ ! -d "data/doc" ]; then
  mkdir -p "data/doc"
fi
docker build -t phil:local -f docker/x64.Dockerfile .
docker run --name philapp phil:local
docker cp philapp:app/data/xlsx extracted
docker cp philapp:app/data/pdf extracted/pdfs
docker logs philapp > logs.txt
docker container rm -f philapp
docker image rm -f phil:local