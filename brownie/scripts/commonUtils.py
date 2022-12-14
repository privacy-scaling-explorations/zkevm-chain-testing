#Contains common utilities for loading external data, reading files, navigating file system etc

import json, sys, os
from pathlib import Path

def getEnv(filename):
    env = json.load(open(filename))
    return env

def loadMap(filename):
    map =  json.load(open())
    return map

def getProjectDir(env):
    current=Path(os.getcwd())
    pdir = [i for i in current.parents if str(i).endswith(env['parentDir'])]
    if len(pdir) == 1:
        return pdir[0]
    else: 
        print("Error: could not determine brownie project location")
        sys.exit(1)

#This one is probably not used - will be deprecated in some next iteration
def getUserInputs(env):
    testEnvs = env["testEnvironments"].split()
    print("Select test environment\n(just hit enter for REPLICA, otherwise K8 or TESTNET):\n")
    for i in range(len(testEnvs)):
        print(f"{i} : {testEnvs[i]}")
    testenv = testEnvs[int(input("insert environment index:") or 1)]

def loadJson(filename):
    '''
    Returns a dict object from selected json file. 
    '''
    map =  json.load(open(filename))
    return map

