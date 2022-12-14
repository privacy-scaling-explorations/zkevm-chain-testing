#!/bin/bash
set -e
set -x

cwd=$(pwd)
d=$(date +"%Y%m%d")
ln -sfn ./chain/$d zkevm-chain
git clone https://github.com/appliedzkp/zkevm-chain.git ./chain/$d

python3 add-test-accounts.py $cwd/test-accounts.json $cwd/zkevm-chain/docker/geth/templates/l1-testnet.json

mv l1-testnet.json $cwd/chain/$d/docker/geth/templates/

cd zkevm-chain

mv .env.example .env
sed -i "s|- 8000:8000|- 80:8000|" docker-compose-pub.yml
sed -i "s|- COORDINATOR_DUMMY_PROVER=\${COORDINATOR_DUMMY_PROVER:-true}|- COORDINATOR_DUMMY_PROVER=\${COORDINATOR_DUMMY_PROVER:-false}|" docker-compose.yml
sed -i "s|- COORDINATOR_UNSAFE_RPC=\${COORDINATOR_UNSAFE_RPC:-false}|- COORDINATOR_UNSAFE_RPC=\${COORDINATOR_UNSAFE_RPC:-true}|" docker-compose.yml
DOCKER_BUILDKIT=1 docker compose -f docker-compose.yml -f docker-compose-pub.yml up -d

cd $cwd
docker cp nginx.conf zkevm-chain-web-1:/etc/nginx/nginx.conf
docker restart zkevm-chain-web-1
