
import sys
from inspect import signature,getmembers, isfunction, ismodule
from time import sleep
from scripts.circuitUtils import opCodes
from scripts.chainTests import test_calibrateOpCode, test_benchProof, test_calculateBlockCircuitCosts
from scripts.tools import request_proof, flush_prover, request_prover_tasks, get_config, set_config, current_block
from scripts import chainTests, circuitUtils, rpcUtils, debugUtils, prover
from types import ModuleType
from pprint import pprint

# from scripts.w3Utils import sendTx, getTxTrace

def get_help(methodName):
    '''
    To display a list with available tests, type: <brownie run scripts/globals.py main showTests 
    --network {network-name, for example zkevmchain}>

    For a list of available tools/utilities, type <brownie run scripts/globals.py main showTools 
    --network {network-name, for example zkevmchain}>
    
    '''

    if methodName != '':
        print(help(methodName))

def getMembers(largs):
    lcl = globals()
    root_module = lcl['scripts']
    modules = getmembers(root_module)
    return modules
    
def showMethods(largs):
    '''
    Displays all Available Methods
    '''
    g = globals()
    c = [i for i in g.keys() if callable(g[i])]
    # c = [i for i in c if 'test_' in i]
    # print(f"Available Methods:{c}")
    called_methods = [i for i in largs if i in c]
    if len(called_methods) == 0:
        raise Exception("No valid method/function was called!")
    return called_methods

def showTests(largs):
    '''
    Displays all implemented Tests
    '''
    g = globals()
    c = [i for i in g.keys() if callable(g[i])]
    c = [i for i in c if 'test_' in i]
    print(f"Available Tests:{c}")

    called_methods = [i for i in largs if i in c]

    return called_methods


def showTools(largs):
    '''
    Displays all callable tools that belong to a selected module
    '''
    print(largs)
    l = globals()
    tools = {i:l[i] for i in l.keys() if isinstance(l[i], ModuleType)}
    pprint(tools)
    return tools

def getFuncInstance(userInput):
    '''
    Returns a function instance using user input as function name. function is selected
    from globals dict as globals()[sys.argv[<index>]]
    Return 1. 
        the function instance if object exists, None if it does not exist.
        Will print the function docstring if it exists but function call failed (due 
        to incorrect args etc)
    Return 2. 
        the number of required function inputs
    '''

    # Is Callable
    g = globals()
    c = [i for i in g.keys() if callable(g[i])]
    exists = userInput in c

    if exists:
        try:
            funcInstance = g[userInput]
            sig = signature(funcInstance)
            numOfInputs = len(sig.parameters.keys())
        except:
            print(help(funcInstance))
            funcInstance = None
            numOfInputs = None
    else:
        funcInstance = None
        numOfInputs = None
        print(f"function does not exist!\nSelect a proper function according to below list:\n{c}")
        # sys.exit(1)
        
    return funcInstance, numOfInputs

# from helpers import as:


def show_Contracts():
    pass

