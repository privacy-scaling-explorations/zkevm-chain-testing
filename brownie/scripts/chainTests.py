from scripts.w3Utils import setupW3Provider, loadContract, getScName, sendTx
from scripts.debugUtils import getTxTraceByBlock, getTxTraceByHash, getTxTraceFromTxObject, getBlockInfo
from scripts.prover import proof_request, queryProverTasks, flushTasks
from scripts.circuitUtils import opCodes, calcTxCosts
from scripts.tools import request_proof, request_prover_tasks
from time import sleep

from pprint import pprint

def test_calibrateOpCode(lcl, circuit, iterations=100, layer=2):
    '''
    Calculates the maximum number of worst case opcode executions that satisfies BLOCK_GAS_LIMIT
    Requires inputs:
    1. circuit: string > one of [EVM, STATE, etc]
    2. iterations: integer, start form a sufficienctly large value (for example 100000)to exceed gas limit
    Script will then repeat with steps of (minus )-1000 until block gas complies
    3. testenv: string, defaults to 'REPLICA', see environment.json for other options
    4. layer: integer, defaults to 2, for now no need to consider layer 1
    NOTE:Make sure to run this test with coordinator config option "dummy_proof" set to true to avoid spamming prover
    with unessecary proof requests
    example:
    brownie run scripts/globals.py main calibrateOpCode STATE 80000 --network zkevmchain

    >> lcl input referes to the locals() dict that is passed from the main script as *args (see method call: methodInstance(*([locals()]+paramsExpected)))
    '''
    testenv=lcl['env']['testEnvironment']
    url = lcl['env']["rpcUrls"][f'{testenv}'"_BASE"]+f"l{layer}"
    w3, chainid = setupW3Provider(url,testenv, layer)
    contractName, opCode = getScName(circuit)[0], getScName(circuit)[1]
    jsonmap = lcl['jsonmap']
    sc = loadContract(jsonmap, chainid,contractName)
    txNotSent = True
    iterations = int(iterations)
    while txNotSent:
        print(f"Submitting transaction with {iterations} calls of worst case opcode ({opCode}) for {circuit} circuit")
        tx, txNotSent = sendTx(iterations,sc,lcl['owner'])
        
        if not txNotSent:
            block = tx.block_number
            print(f"Transaction with {iterations} executions of opcode is submitted in block: {block}. Tx cost is {tx.gas_used}")
            # txNotSent = False
        else:
            iterations -= 1000

    return iterations
    
def test_benchProof(lcl,circuit,iterations=100, proof_options="", abort=False, flush=False, retry=False, layer=2):
    '''
    Test Sequence: 
    1. Checks if there is ongoing proof task via the info method
    2. Waits until there are no pending/ongoing tasks (of flushes everything if flush=True)
    3. Sends a Tx to invoke the contract in question, according to target circuit
    4. Retrieves the block number where the tx was submitted and audits the block proof state
    until proof is generated or an error occurs

    Inputs:
        -   circuits: EVM, STATE
        -   iterations: the max number of opcode steps that satisfies gasUsed < 300K (exec test_calibrateOpCode
            to get this number)
        -   proof_options: defaults to proofOptions.json, otherwise input a string of the form:
            "aggregate True circuit super"

            for example:
                #brownie run scripts/globals.py  main test_benchProof EVM 100 "aggregate True circuit pi" --network zkEVM-chain-maronis-l2
        -   retry: (bool) defines whether prover reattempts a failed proof. Must be False for test purpose
        -   flush: (bool) use it to clear tasks cache before starting bench
        -   abort: (bool) set to true if you want to abort the test in case prover is busy with ongoing task

    Result:
        - proof and proof generation duration
    '''
    testenv=lcl['env']['testEnvironment']
    url = lcl['env']["rpcUrls"][f'{testenv}'"_BASE"]+f"l{layer}"
    w3, chainid = setupW3Provider(url,testenv, layer)
    contractName, opCode = getScName(circuit)[0], getScName(circuit)[1]
    jsonmap = lcl['jsonmap']
    sc = loadContract(jsonmap, chainid,contractName)
    txNotSent = True
    iterations = int(iterations)
    retry = str(retry).lower()
    proverUrl = lcl['env']["rpcUrls"][f'{testenv}'"_BASE"]+"prover"
    sourceUrl = lcl['SOURCE_URL']

    # put rpc call to info method here

    if flush:
        print("Flushing Tasks")
        flushTasks(proverUrl,True,True,True,1)

    isIdle,isBusy,tasks = request_prover_tasks(lcl)
    print('Waiting active and queued tasks to finish')
    while not isIdle:
        sleep(60)
        isIdle,isBusy,tasks = request_prover_tasks(lcl)
 
    while txNotSent:
        print(f"Submitting transaction with {iterations} calls of worst case opcode ({opCode}) for {circuit} circuit")
        tx, txNotSent = sendTx(iterations,sc,lcl['owner'])
        
   
    block = tx.block_number
    print(f"Transaction with {iterations} executions of opcode is submitted in block: {block}. Tx cost is {tx.gas_used}")

    print(f'Sending proof request for block {block} ')
    error = False
    task_completed = False
    request_proof(lcl,block,proof_options)
    print(f'Submitted proof request for block {block}')
    while not error and not task_completed:
        task = request_prover_tasks(lcl,block)
        task = task[-1]

        task_completed = bool(task['result'])
        if task_completed:
            try:
                error = 'Err' in task['result'].keys()
            except:
                pass
        if error:
            error_message = task['result']['Err']
        if not task_completed:
            sleep(60)
    try:
        print(f'Error: {error_message}')
    except:
        pass

    proofs = task["result"]["Ok"]

    metrics = {
                "Block":block,
                "Duration": {
                            "Aggregation" :proofs['aggregation']['duration'],  
                            "Circuit"     :proofs['circuit']['duration']
                },
                "Config": proofs['config']
            }

    pprint(metrics)
    return metrics



def test_calculateBlockCircuitCosts(lcl, blocknumber, dumpTxTrace=False, layer=2):
    '''
    Enter doc strings here
    '''
    testenv=lcl['env']['testEnvironment']
    url = lcl['env']["rpcUrls"][f'{testenv}'"_BASE"]+f"l{layer}"
    w3, chainid = setupW3Provider(url,testenv, layer)
    jsonmap = lcl['jsonmap']

    bl = getBlockInfo(w3,blocknumber)
    txHases = [i['hash'] for i in bl.transactions]
        
