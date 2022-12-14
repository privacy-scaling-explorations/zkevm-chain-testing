#!/bin/bash
set -x
set -e

USER=$(whoami)
ENV_FILE_NAME="environment.json"
BROWNIE="/home/$USER/.local/bin/brownie"
WORKING_DIR_NAME=$(basename $(pwd))
JENKINS_USER=$1
CHAIN_ID_L2=$2
IP_ADDRESS=$3
CHAIN_ID_L1=$4

if [ ! $WORKING_DIR_NAME = "brownie" ]; then
    echo "Run this script from the brownie directory"
    exit 1
fi

if [ $# -ne 4 ]; then
    echo "Please provide all the necessary arguments, ie: prepare.sh <username> <chainid-l2> <ipaddress> <chainid-l1>"
    exit 1
fi

install_pkgs() {
    sudo apt-get update
    sudo apt-get install jq python3.10-venv python3-pip -y 
    python3 -m pip install --user pipx
    python3 -m pipx ensurepath
}

install_brownie() {
#    /home/$USER/.local/bin/pipx install eth-brownie
#    /home/$USER/.local/bin/pipx inject eth-brownie pandas
     pip3 install eth-brownie
     pip3 install pandas
    source ~/.bashrc
}

add_network() {
   sed -i "s/username/${JENKINS_USER}/;s/ip-address/${IP_ADDRESS}/g" $ENV_FILE_NAME
   URL=$(jq -r .rpcUrls.${JENKINS_USER}_BASE $ENV_FILE_NAME)
   $BROWNIE networks add zkevm-chain-l2 zkEVM-chain-${JENKINS_USER}-l2 host=$URL"l2" chainid=$CHAIN_ID_L2
   $BROWNIE networks add zkevm-chain-l1 zkEVM-chain-${JENKINS_USER}-l1 host=$URL"l1" chainid=$CHAIN_ID_L1
}

run_brownie () {
    brownie compile
    brownie run scripts/deploy.py --network ${NETWORK_ID}_BASE
}

#Not needed anymore. Will remove in future release
run_brownie_test () {
    brownie run scripts/client.py --network ${NETWORK_ID}_BASE
}

main() {
    if [ ! -f $BROWNIE ]; then
        install_pkgs
        install_brownie
        add_network
        # run_brownie
        #run_brownie_test
    else
        echo "Nothing to do here. Brownie is all set. Go on start testing"
    fi
}

main
    
exit 0
