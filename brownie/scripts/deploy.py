from brownie import CheckSdiv,CheckMload
from brownie.network import accounts
from web3 import Web3
from pathlib import Path
from scripts import commonUtils as cu 
import os

envfile = "environment.json"
env = cu.getEnv(envfile)
projectDir = cu.getProjectDir(env)
keyfilesDir = projectDir.joinpath(env["keystoredir"])
deploymentsDir = projectDir.joinpath(f'brownie/{env["deployments"]}')

def main():
    keyfiles = [i for i in os.listdir(keyfilesDir) if "UTC" in i]
    print(keyfiles)
    print(f"{keyfilesDir}{keyfiles[0]}")
    accounts.load(f"{keyfilesDir}/{keyfiles[0]}", "password")
    owner = accounts[0]
  
    checksdiv = CheckSdiv.deploy({"from": owner})
    checkmload = CheckMload.deploy({"from": owner})
