#!/bin/bash
set -x

/home/ubuntu/.local/bin/brownie networks delete zkEVM-chain-maronis-l1
/home/ubuntu/.local/bin/brownie networks delete zkEVM-chain-maronis-l2

pipx uninstall-all
docker rm -f gotest
#rm -rf zkevm-chain-testing
rm -rf taframework
