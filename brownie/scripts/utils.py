# from brownie import Check5
from brownie import CheckSdiv, CheckMload
from brownie.network import accounts
from web3 import Web3
from pathlib import Path
import time, os, json, sys, requests
import pandas as pd
from pprint import pprint


def getEnv(filename):
    env = json.load(open(filename))
    return env

def getUserInputs(env):
    circuit = input("Circuit to run benchmark against")
    provers = int(input("Number of prover replicas: "))
    calibrate = input("calibrate opcode? (True/False) :") == "True"
    op = input('opcode: ') or 'MULMOD'
    testEnvs = env["testEnvironments"].split()
    print("Select test environment\n(just hit enter for REPLICA, otherwise K8 or TESTNET):\n")
    for i in range(len(testEnvs)):
        print(f"{i} : {testEnvs[i]}")
    testenv = testEnvs[int(input("insert environment index:") or 1)]
    d = [ int(i) for i in env["degrees"].split() ]
    degree = int(input("Select circuit degree. Must match the value PARAMS_PATH in coordinator service at docker compose file: \n"))
    proof = input("query proofs? (True/False) :") == "True" 
    if not calibrate:
        numOfiterations = int(input("start number of opcode iterations: "))
    else:
        numOfiterations = None
    step = int(input("step: "))
    try:
        stop = int(input("stop at: "))
    except:
        stop = 10000000
        print("No hard stop was provided. Will run until interrupted with CTRL-C or a proof failure occurs")
    
    return circuit, provers, calibrate, op, d,testenv, degree,proof, numOfiterations, step, stop

  
def opCodes():
    '''
    Loads a pandas dataframe with implemented opcodes vs gas/circuit cost
    '''
    op = pd.read_csv('opcodesEVM',sep='|')
    op=op.set_index('opcode')

    return op

# def getUser():
#     user = os.getlogin()
#     return user


def loadMap(filename):
    map =  json.load(open())
    return map

def Contracts(map):
    contracts = {}
    networks = map.keys()
    for net in networks:
        contracts[net] = []
    for net in contracts.keys():
        for ctr in map[net].keys():
            contracts[net].append(ctr)
    return contracts


def getProjectDir(env):
    current=Path(os.getcwd())
    pdir = [i for i in current.parents if str(i).endswith(env['parentDir'])]
    if len(pdir) == 1:
        return pdir[0]
    else: 
        print("Error: could not determine brownie project location")
        sys.exit(1)

def sendTx(numOfiterations,contractInstance,owner):
    tx = contractInstance.checkBatchYul(((numOfiterations),),{"from": owner})
    
    return tx

def getTxTrace(tx):
    traceDone = False
    while not traceDone:
        try:
            tr = tx.trace
            traceDone = True
            print('Tx trace done')
        except:
            print("failed to get tx trace")
    
    return tr

def getBlockGasCostFromTrace(tx,txtrace):
    gas_used = tx.gas_used
    print(gas_used)
    gasFromTrace = sum([i['gasCost'] for i in txtrace])
    print(gasFromTrace)
    print(gas_used-gasFromTrace)


def getOCsGasCost(oc, txtrace):
    gasFromOC = sum([i['gasCost'] for i in txtrace if i['op'] == oc])

    return gasFromOC

def getBlockCircuitCostFromOCs(opcodes,txtrace, op=''):
    '''Calculates the total block circuit cost. If opcode (op) is defined,
       function also returns the circuit cost contribution of the given opcode
       Takes in the opcodes dataframe from  opCodes(), a Tx trace and an opcode as
       a string
    '''
    
    totalBlockCircuitCost = sum([opcodes.loc[i['op']]['h'] for i in txtrace])
    if op:
        OpCircuitCost = sum([opcodes.loc[i['op']]['h'] for i in txtrace if i['op'] == op])
    else:
        OpCircuitCost = None

    return totalBlockCircuitCost,OpCircuitCost

def processTxTrace(opcode,trace, opcodesDF):
    opsexecuted = [i['op'] for i in trace]
    opcodeH = sum([opcodesDF.loc[op]['h'] for op in opsexecuted if op==opcode])
    blockH = sum([opcodesDF.loc[op]['h'] for op in opsexecuted])
    opcodeG = sum([opcodesDF.loc[op]['g'] for op in opsexecuted if op==opcode])
    blockG = sum([opcodesDF.loc[op]['g'] for op in opsexecuted])
    
    return opcodeH, blockH, opcodeG, blockG

def getProverTasks(proverUrl):
    '''
    returns true if there are ongoing proofs (tasks with 'result' == None)
    '''
    data=f'{{"jsonrpc":"2.0", "method":"info", "params":[], "id":1}}'
    r = requests.post(proverUrl,data)
    tasks = r.json()['result']['tasks']
    ongoingProofs = bool(len([ i['result'] for i in tasks if i["result"]==None]))
    return ongoingProofs

def calcTxCosts(circuit,trace,op,df):
    '''
    Returns total block gas/h per transaction and opcode gas/h per transaction. Takes in circuit (EVM,STATE, etc) opcode 
    name (SDIV, MLOAD etc), tx trace and opcodes circuit costs dataframe (need to load the CircuitCosts.csv with pandas)  
    '''
    TxG = sum([pc['gasCost'] for pc in trace]) 
    opCount = len([pc for pc in trace if pc['op'] == op])
    opTxG = int(df.loc[op][f'g{circuit}']*opCount)
    gRatio = opTxG/TxG
    TxH = int(sum([df.loc[pc['op']][f'h{circuit}'] for pc in trace]))
    opTxH = int(df.loc[op][f'h{circuit}']*opCount)
    hRatio = opTxH/TxH
    print(f' txG: {TxG}\n opCount: {opCount}\n opTxG: {opTxG}\n TxH: {TxH}\n opTxH: {opTxH}\n hRatio: {hRatio}\n gRatio: {gRatio}')

    return TxG,opCount,opTxG,TxH,opTxH, hRatio, gRatio

def getProofState(proverUrl,sourceURL,tx,degree,numOfiterations,resultsDir,tr,op,step,opcodeDF):
    stepResult = {}
    stepResult["OpCodes"] = numOfiterations
    stepResult["Block"] = tx.block_number
    stepResult["GasUsed"] = tx.gas_used
    stepResult[f"{op}-h"],stepResult["TotalBlock-h"], stepResult["OpcodeGasFromTrace"], stepResult["TxGasFromTrace"] = processTxTrace(op,tr, opcodeDF)
    stepResult[f'%h by {op}'] = stepResult[f"{op}-h"]/stepResult["TotalBlock-h"]
    data=f'{{"jsonrpc":"2.0", "method":"proof", "params":[{{"block":{tx.block_number},"rpc":"{sourceURL}", "retry":false, "param": "/testnet/{degree}.bin"}}], "id":{tx.block_number}}}'
    proofCompleted = False
    while not proofCompleted:
        # print(f"Waiting for block {tx.block_number} proof")
        r = requests.post(proverUrl,data)
        error = 'error' in r.json().keys()
        # pprint(r.json())
        if tx.gas_used > 1000000:
            print('Exceeded block gas limit. Stopping test')
            proofCompleted = True
            proofFailed = True
            stepResult["Error"] = "Block Gas-Limit exceeded"
        elif error:
            print(f'ERROR: Block: {tx.block_number} -- {r.json()["error"]}')
            proofCompleted = True
            proofFailed = error
            stepResult["Error"] = r.json()["error"]
        elif 'result' in r.json().keys():
            proofFailed = False
            result = r.json()['result']
            proofCompleted = result != None
            if proofCompleted:
                # stop = int(time.time())
                # with open(f'{resultsDir}/TxTrace{op}_{numOfiterations}.json', 'w') as writeme:
                #     json.dump(tr, writeme)
                duration = r.json()["result"]["duration"]/1000
                stepResult["ProofDuration"] = duration
                mins = (duration - duration%60)/60
                pprint(r.json()['result'])
                # print(f'Proof for block {tx.block_number} generated in {mins} minutes and {duration - 60*mins} seconds\n{r.json()["result"]}')
                print(f'Proof for block {tx.block_number} with {numOfiterations} {op}s : generated in {mins} minutes and {duration - 60*mins} seconds')


    return stepResult,proofCompleted,proofFailed