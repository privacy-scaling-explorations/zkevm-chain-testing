from scripts.coordinator import fetch_coordinator_config
from scripts.prover import proof_request, queryProverTasks, flushTasks,proof_options
from scripts.w3Utils import sendTx, loadContract, setupW3Provider, getScName, getBlockNumber, dispatchMessage, loadAccount, loadPreCompiledContract, getBalances
from scripts.circuitUtils import calcTxCosts
from scripts.debugUtils import getBlockInfo, getTxTraceByHash
import scripts.reporting as reporting
from brownie import chain
from web3 import Web3
import json
from pprint import pprint
from web3 import Web3
from brownie import chain
import json
from random import randrange
# import scripts.commonUtils as cu
import sys
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

def update_results_db(lcl,test_id,table,dummy=False):
   
    statsDir = lcl['statsdir']
    env         = lcl["env"]
    pgsqldb     = env["reporting"]["db"]
    grafana_url = env["grafana-dashboard-prefix"]
    engine = reporting.pgsql_engine(pgsqldb)

    print(f'Updating table {table}')
    try:
        cpu_statistics,cpus = reporting.write_test_post_data(engine, grafana_url, test_id, table, statsDir)
    except Exception as e:
        print(e)

    print('Updating table testresults_cpustat')
    try:
        reporting.write_perCore_stats(engine, cpu_statistics, cpus,test_id, dummy)
    except Exception as e:
        print(e)

def tracesByBlock(lcl, testenv, blocknumber, layer, dump=False):
    try:
        env = lcl["env"]
        url = env["rpcUrls"][f'{testenv}'"_BASE"]+f"l{layer}"
        w3, cid = setupW3Provider(url,testenv,layer)
    except Exception as e:
        print(e)
    try:
        blockObj =  getBlockInfo(w3,int(blocknumber))
    except Exception as e:
        print(e)
    transactions = blockObj.transactions
    for tx in transactions:
        txHash = tx['hash'].hex()
        print(txHash)
        try:
            txTrace = getTxTraceByHash(chain,txHash,True)
        except Exception as e:
            print(e)
        txTrace = getTxTraceByHash(chain,txHash,False)
        try:
            if dump:
                filename = f'Block_{blocknumber}-Tx_{txHash}.txtrace'
                with open(filename,'w') as writeme:
                    json.dump(txTrace,writeme,indent=4)
        except Exception as e:
            print(e)

def request_proof(lcl,block,proofoptions=""):
    '''
    Standalone Utility to start a proving task for a given block,

    Takes in the block number integer, and proof request options (proofoptions) as string
    Defaults to empty string, proofoptions="" >> defaults (see proofOptions.json) 
    
    example:

     brownie run scripts/globals.py main request_proof 1 --network zkevmchain

     or 

     #brownie run scripts/globals.py main request_proof 1 "aggregate True retry True circuit pi"--network zkevmchain
    '''
    testenv=lcl['env']['testEnvironment']
    proverUrl = lcl['env']["rpcUrls"][f'{testenv}'"_BASE"]+"prover"
    sourceUrl = lcl['SOURCE_URL']

    options = proof_options(proofoptions)
    aggregate = str(options['aggregate']).lower()
    mock_feedback = str(options['mock_feedback']).lower()
    mock = str(options['mock']).lower()
    retry = str(options['retry']).lower()
    circuit = options['circuit']

    result = proof_request(proverUrl,mock,aggregate,mock_feedback,int(block),sourceUrl,retry,circuit)

def request_prover_tasks(lcl, block=0, _print=False):
    '''
    Standalone Ultility to query prover node(s) for proof tasks status
    Set the block variable to query the proof status for a submitted block
    example:

    This will return all existing tasks' state (Ok/Err/None) (cached, pending, completed) and prover state (idle or busy)
        #brownie run scripts/globals.py main  queryProverTasks --network zkevmchain

    This will only return the proof task status/result for block 10
        #brownie run scripts/globals.py main  queryProverTasks 10 --network zkevmchain
    
    set _print to True to display the result in stdout
    '''
    testenv=lcl['env']['testEnvironment']
    proverUrl = lcl['env']["rpcUrls"][f'{testenv}'"_BASE"]+"prover"
    if int(block) == 0:
        isIdle, isBusy, tasks  = queryProverTasks(proverUrl)
        result = (isIdle, isBusy, tasks)
        if _print:
            pprint(result)
        return isIdle, isBusy, tasks
    else:
        blockResult = queryProverTasks(proverUrl,block)
        result = blockResult
        try:
            proofs = result[-1]["result"]["Ok"]
            metrics = {
                    "Block"       : block,
                    "Aggregation" : {
                                      "duration" : proofs['aggregation']['duration'],
                                      "k"        : proofs['aggregation']['k'] 
                                    }, 
                    "Circuit"     : {
                                      "duration" : proofs['circuit']['duration'],
                                      "k"        : proofs['circuit']['k']
                                    },      
                    "Gas"         : proofs['gas'],
                    "Config"      : proofs['config']
                    }

            if _print:
                pprint(metrics)
        except:
            try:
                error = result[-1]["result"]["Err"]
                metrics = {
                    "Block" : block,
                    "Error" : error
                }
                if _print:
                    pprint(metrics)
            except:
                if _print:
                    pprint(result)

        return result

def flush_prover(lcl,cache,pending,completed):
    '''
    Standalone Ultility to flush prover node(s) tasks' register

    example:

    brownie run scripts/globals.py main  flush_prover --network zkevmchain
    '''
    testenv=lcl['env']['testEnvironment']
    cache=str(cache).lower()
    pending=str(pending).lower()
    completed=str(completed).lower()
    proverUrl = lcl['env']["rpcUrls"][f'{testenv}'"_BASE"]+"prover"

    result = flushTasks(proverUrl,cache,pending,completed)

def get_config(lcl,node="coordinator", params=f'[]', print_result=True):
    testenv=lcl['env']['testEnvironment']
    coordinator_url = lcl['env']["rpcUrls"][f'{testenv}'"_BASE"]+f'{node}'
    result = fetch_coordinator_config(coordinator_url, params)
    if print_result:
        try:
            pprint(result.json()['result'])
        except:
            pprint(result)
    try:
        return result.json()['result']
    except:
        return result

################################################################################
# This is the correct format of the params argument within the config rpc method
#  params=f'[{{"dummy_prover":true,\
#     "mock_prover":false,\
#     "mock_prover_if_error":false,\
#     "unsafe_rpc":true,\
#     "rpc_server_nodes":"server-testnet-geth:8545",\
#     "enable_faucet":true,\
#     "listen":"[::]:8545",\
#     "l1_rpc_url":"http://l1-testnet-geth:8545/",\
#     "l1_bridge":"0x936a70c0b28532aa22240dce21f89a8399d6ac60",\
#     "aggregate_proof":false,\
#     "circuit_name": "pi",\
#     "l1_priv":"2bdd21761a483f71054e14f5b827213567971c676928d9a1808cbfa4b7501200",\
#     "l2_rpc_url":"http://leader-testnet-geth:8545/",\
#     "params_path":"/testnet/",\
#     "prover_rpcd_url":"http://prover-rpcd:8545/"\
#     }}]'
#####################################################################################

def set_config(lcl, params):
    '''
    Can be used to modify the coordinator configuration post deployment.
    input: a string of the form "a valueOf(a) b valueOf(b) ....", for example:
    "aggregate true dummy_prover true mock false circuit_name super".
    NOTE: a, b, c etc must be keys belonging to the struct returned by get_config
    '''
    params_dict = get_config(lcl,print_result=False)
    #Create a list with user inputs and validate
    p=params.split()
    if len(p)%2 !=0:
        print("Error: Number of inputs must be even")
    else:
        even_indexes = [i for i in range(len(p)) if i%2 == 0]
        # check if provided fields belong to the config struct:
        fields_l = list(params_dict.keys())
        fields_s = set(fields_l)
        new_fields_l = [p[i] for i in even_indexes]
        #Determin what config fields should be changed and make sure they re part of the config struct
        new_fields_s = set(new_fields_l)

        diff = new_fields_s.difference(fields_s)
        if len(diff) != 0:
            print(f"Error: Provided inputs {[i for i in list(diff)]} are not config struct members. Exiting.")
        else:
            #Replace new values
            for index in even_indexes:
                print(f'{p[index]} : {params_dict[p[index]]} >> {p[index+1]}')
                params_dict[p[index]] = p[index+1]
                # print(f'{p[index]}:{p[index+1]}')

        del params_dict["params_path"]
        #Create a list from resulting dictionary and format
        params_list = ["[{"]
        for param in params_dict.keys():
            if params_dict[param] in [True, False,'true', 'false']:
                # element = '"'+param+'"'+":"+str(params_dict[param]).lower().rstrip()
                element = f'"{param}":{str(params_dict[param]).lower().rstrip()}'
            else:
                # element = '"'+param+'"'+":"+'"'+params_dict[param]+'"'
                element = f'"{param}":"{params_dict[param]}"'

            params_list.append(element)
        params_list.append("}]")

        try:
            new_params = ", ".join(params_list).replace(",","",1)
            new_params_rev = new_params[::-1]
            new_params_rev = new_params_rev.replace(",","",1)
            new_params = new_params_rev[::-1]
        except Exception as e:
            print(e)
        #Invoke the config method with new configuration parameters
        get_config(lcl,params=new_params,print_result=False)

def sendTransaction(lcl, layer=2):
    pass

def current_block(lcl, layer):
    testenv=lcl['env']['testEnvironment']
    url = lcl['env']["rpcUrls"][f'{testenv}'"_BASE"]+f"l{layer}"
    w3, cid = setupW3Provider(url,testenv,layer)

    block = getBlockNumber(w3)
    print(f"Current Block: {block}")
    return block


def sendEthToL2(lcl,layer):
    kfdir   = lcl["keyfilesDir"]
    kfiles = lcl["keyfiles"] 
    b_address = lcl["env"][f"L{layer}BRIDGE"]["address"]
    b_abi = lcl["env"][f"L{layer}BRIDGE"]["abi"]
    precomp_folder = lcl["env"]["precompilesFolder"]
    for kfile in kfiles:
        kf = f'{kfdir}/{kfile}'
        accounts = loadAccount(kf,"password")
    precompDir = lcl["projectDir"].joinpath(f'brownie/{precomp_folder}')
    bridge = loadPreCompiledContract(b_address,f"{precompDir}/{b_abi}", "bridge")
    blocks=[]
    for acc in accounts:
        addr = acc.address
        tx=bridge.dispatchMessage(addr, 0, "0xffffffffffffffff", acc.nonce, "0x",{'from': acc, 'value': 999999999999999999999999999})
        blocks.append(tx.block_number)

    return blocks

        
def get_Balances(lcl):
    kfdir   = lcl["keyfilesDir"]
    kfiles = lcl["keyfiles"] 
    for kfile in kfiles:
        kf = f'{kfdir}/{kfile}'
        accounts = loadAccount(kf,"password")
    balances = getBalances(accounts)
    pprint(balances)
    return balances

def crossChainTx(lcl,layer):
    try:
        kfdir   = lcl["keyfilesDir"]
        kfiles = lcl["keyfiles"] 
        b_address = lcl["env"][f"L{layer}BRIDGE"]["address"]
        b_abi = lcl["env"][f"L{layer}BRIDGE"]["abi"]
        precomp_folder = lcl["env"]["precompilesFolder"]
        for kfile in kfiles:
            kf = f'{kfdir}/{kfile}'
            accounts = loadAccount(kf,"password")
        precompDir = lcl["projectDir"].joinpath(f'brownie/{precomp_folder}')
        bridge = loadPreCompiledContract(b_address,f"{precompDir}/{b_abi}", "bridge")
        acc=accounts[randrange(len(accounts))]
        addr = acc.address
    except Exception as e:
        print(e)
    try:
        tx=bridge.dispatchMessage(addr, 0, "0xffffffffffffffff", acc.nonce, "0x",{'from': acc, 'value': 999999})
        txNotSent=False
    except Exception as e:
        print(e)
        txNotSent=True
    return tx, txNotSent
