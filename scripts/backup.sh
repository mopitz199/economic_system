#!/bin/sh

timestamp() {
  date +"%s"
}

postgres_container_id=$(docker ps | grep 'postgres' | awk '{ print $1 }')
web_container_id=$(docker ps | grep 'web' | awk '{ print $1 }')

base_path=$(pwd)
cd /mnt/volume_nyc1_01/src/economic_system/backups/

file_name=$(timestamp)
docker exec ${postgres_container_id} pg_dump -U admin economic_system>${file_name}

docker exec ${web_container_id} aws s3 cp backups/${file_name} s3://economicapp-db-backups

rm ${file_name}