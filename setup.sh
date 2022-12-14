#!/bin/bash
#
set -e
set -x

wdir=$(pwd)
user=$(id -un 1000)
ENV_FILE_NAME=$wdir/go-client/.env
JENKINS_USER=$1
IP_ADDRESS=$2

if [ $# -ne 2 ]; then
    echo "Please provide all the necessary arguments, ie: setup.sh <username> <ipaddress>"
    exit 1
fi

sed -i "s/username/${JENKINS_USER}/;s/ip-address/${IP_ADDRESS}/g" $wdir/go-client/.env

git clone https://github.com/google/gofuzz $wdir/go-client/fuzz
# ;)

find $wdir/go-client/fuzz ! -path $wdir/go-client/fuzz ! -name 'fuzz.go' -exec rm -rf {} \; > /dev/null 2>&1 || true

docker run -dit -v $wdir:/Code --name gotest golang
docker exec --workdir /Code/go-client gotest /Code/go_init.sh

sudo chown -R $user:$user $wdir/*

for i in `find $wdir/go-client -mindepth 1 -maxdepth 1 -type d -exec basename {} \;`; do
    pack=${i,,}
    echo "replace $pack v1.0.0 => ./${i,,}" >> $wdir/go-client/go.mod
    #echo "replace $pack v1.0.0 => ./$i" >> $wdir/go.mod
done

docker exec --workdir /Code/go-client gotest go mod tidy
docker exec --workdir /Code/go-client gotest go build .
docker rm -f gotest

sudo chown -R $user:$user $wdir/*
sudo apt install nodejs npm -y
npm install ethers

sed -i "s/ip-address/${IP_ADDRESS}/g" $ENV_FILE_NAME