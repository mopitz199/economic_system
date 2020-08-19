#!/bin/sh

timestamp() {
  date +"%s"
}

postgres_container_id=$(docker ps | grep 'postgres' | awk '{ print $1 }')

cd /efs/

file_name=$(timestamp)
docker exec ${postgres_container_id} pg_dump -U admin economic_system>${file_name}

aws s3 cp ${file_name} s3://economicapp-db-backups

rm -f ${file_name}