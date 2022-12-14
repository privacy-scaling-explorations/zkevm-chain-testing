from scripts.rpcUtils import rpcCall
from pprint import pprint
import scripts.commonUtils as cu
import sys

def proof_options(proofoptions):
    try:
        default_options = cu.loadJson("proofOptions.json")
    except Exception as exc:
        print(exc)
    if proofoptions == "":
        options = default_options
    else:
        opt = proofoptions.split()
        if len(opt) %2 != 0:
            print("Error: Number of inputs must be even")
        else:
            even_indexes = [j for j in range(len(opt)) if j%2==0]
            for index in even_indexes:
                if opt[index] in default_options.keys():
                    default_options[opt[index]] = opt[index+1]
                else:
                    print(f"ERROR: option {opt[index]} is not a valid proofRrequestOptions field")
                    sys.exit(1)

            options = default_options

    return options


def proof_request(proverUrl,mock,aggregate,mock_feedback,block,sourceURL,retry=False,circuit="pi"):
    '''
    Sends a proof_request for selected block, Set the retry boolean to false if: you just need the proof status
    or to invoke a new proof generation without the option to retry in case of failure
    '''

    data = f'{{"jsonrpc":"2.0", "method":"proof", "params":[{{"block":{block},"circuit":"{circuit}","aggregate":{aggregate},"mock":{mock},"mock_feedback":{mock_feedback},"rpc":"{sourceURL}", "retry":{retry}}}], "id":{block}}}'
    pprint(data)
    url=proverUrl
    response = rpcCall(url,data)
    return response

def queryProverTasks(proverUrl, block=0, id=1):
    '''
    Returns the prover task status for a given block if block !=0.
    Otherwise, returns prover status in boolean (isIdle vs isBusy)
    and tasks statuses (struct array) 
    '''
    data=f'{{"jsonrpc":"2.0", "method":"info", "params":[], "id":{id}}}'
    # pprint(data)
    url=proverUrl
    r = rpcCall(url,data)
    response = r.json()
    tasks = response['result']['tasks']
    isIdle = (len(tasks) == 0) or ('None' not in [list(i['result'].keys())[0] if i['result'] else 'None' for i in tasks])
    isBusy =  not isIdle
    if block != 0:
        blockResult = [i for i in tasks if i['options']['block'] == int(block)]  
        return blockResult
    else:
        return isIdle,isBusy, [list(i['result'].keys())[0] if i['result'] else 'None' for i in tasks]

def flushTasks(proverUrl,cache,pending,completed, id=1):
    cache=str(cache).lower()
    pending=str(cache).lower()
    completed=str(cache).lower()
    data = f'{{"jsonrpc":"2.0", "method":"flush", "params":[{{"cache":{cache},"pending":{pending}, "completed":{completed}}}],"id":{id}}}'
    pprint(data)
    url=proverUrl
    response = rpcCall(url,data)
    return response

