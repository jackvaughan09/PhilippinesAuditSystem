FROM jackvaughan/phil:arm64
COPY data /app/data
# Set WD
WORKDIR /app/control
RUN sh run.sh

