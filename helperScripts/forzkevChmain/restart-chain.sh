#!/bin/bash
#set -e
set -x

cwd=$(pwd)
d=$(date +"%Y%m%d")

cd zkevm-chain

docker compose down --volumes
DOCKER_BUILDKIT=1 docker compose up -d

cd $cwd
docker cp nginx.conf zkevm-chain-web-1:/etc/nginx/nginx.conf
docker restart zkevm-chain-web-1
