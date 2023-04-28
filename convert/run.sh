#!/usr/bin/sh
ZIPS="/Users/jackvaughan/Documents/DS/PhilippinesAuditSystem/zips"
PDF="/Users/jackvaughan/Documents/DS/PhilippinesAuditSystem/pdf"

docker build -t convert:local -f convert/convert.Dockerfile .
echo "Running convert:local"
docker run --name convertapp \
  -v $ZIPS:/app/zips \
  -v $PDF:/app/pdf \
  convert:local
docker rm convertapp
docker rmi convert:local
