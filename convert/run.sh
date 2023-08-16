SCRIPTS="/Users/jackvaughan/Documents/DS/PhilippinesAuditSystem/convert"
ROOT=$1

docker build -t convert:local -f ${SCRIPTS}/convert.Dockerfile .
echo "Running convert:local"
docker run --name convertapp \
  -v ${ROOT}:/app/data \
  convert:local
docker rm convertapp
docker rmi convert:local
