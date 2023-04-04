#!bin/bash
docker build -t jackvaughan/phil:arm64 -f docker/arm64-base.Dockerfile .
docker build -t jackvaughan/phil:x64 -f docker/x64-base.Dockerfile .
docker push jackvaughan/phil:arm64
docker push jackvaughan/phil:x64