import sys, os, json
from scripts.helpers import getFuncInstance, get_help, showTests, showTools, showMethods
# from scripts.circuitUtils import opCodes
from time import sleep
import scripts.commonUtils as cu
from pprint import pprint
from brownie.network import accounts
from web3 import Web3
from web3.middleware import geth_poa_middleware


def main(*args):
    largs = list(args)
    # print(largs)

    if len(largs) < 1:
        print("Insufficient number of inputs.")
        sleep(2)
        print(help(get_help))
        sys.exit(1)


    else:
        # All variables listed here are handled as inputs to various callables, via locals() dict. 
        # Maybe consider adding a helper function to return those values in oneliner
        BLOCK_GAS_LIMIT = 300000
        SOURCE_URL = "http://leader-testnet-geth:8545/"
        envfile = "environment.json"
        env = cu.getEnv(envfile)
        testenv=env['testEnvironment']
        projectDir = cu.getProjectDir(env)
        keyfilesDir = projectDir.joinpath(env["keystoredir"])
        deploymentsDir = projectDir.joinpath(f'brownie/{env["deployments"]}')
        resultsDir = projectDir.joinpath(f'brownie/{env["resultsdir"]}')    
        keyfiles = [i for i in os.listdir(keyfilesDir) if "UTC" in i]
        accounts.load(f"{keyfilesDir}/{keyfiles[0]}", "password")
        owner = accounts[0]
        jsonmap = json.load(open(f"{projectDir}/brownie/{env['deployments']}/map.json"))
        user = os.getlogin()
        # pprint(locals())
        # print("++++++++++++++++++++++++++++++++++++")

        # TODO: THROW ERROR IN CASE A LOT OF ARGUMENTS 
        # TODO: IF ARGUMENT NAME MATHCES A CALLABLE NAME, SCRIPT WILL FAIL
        called_methods = showMethods(largs)
        # print(f"input args:{largs}")
        # print(f"called methods:{called_methods}")
        # largs_method_indexes = [largs.index(i) for i in called_methods]
        # print(largs_method_indexes)

        for method in called_methods:
            # print(method)
            largs_method_index = largs.index(method)
            methodInstance, nofargs = getFuncInstance(method)
            # print(nofargs)
            if methodInstance:
                try:
                    paramsExpected = largs[largs_method_index + 1 : largs_method_index + 1 + nofargs]
                    # numOfparamsGiven =  largs_method_indexes[largs.index(method) + 1] -   [largs.index(method)]
                    # paramsExpected = None
                    methodInstance(*([locals()]+paramsExpected))
                except:
                    print(f"Error instantiating method {method}")
                    sleep(2)
                    print(help(methodInstance))
                    sys.exit(1)
            else:
                raise Exception(f"Error instantiating method {method}")

