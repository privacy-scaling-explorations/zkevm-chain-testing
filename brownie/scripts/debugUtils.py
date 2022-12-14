import json
from pathlib import Path
from unittest import case

def getTxTraceFromTxObject(resultsDir,tx, dump=False):
    '''
    Takes in a tx trace object as input and returns the transaction object.
    Optional: set dump to True >> writes the trace to disk (in .json)
    '''
    traceDone = False
    # while not traceDone:
    try:
        tr = tx.trace
        traceDone = True
        print('Tx trace done')
    except Exception as e:
        print(f"failed to get tx trace due to <<{e}>>")
        tr = {}
        
    if dump and traceDone:
        f = f"Block_{tx.block_number}_Tx_{tx.txid}"
        writeTestResult(tr,f, resultsDir)

    return tr

def getBlockInfo(httpProvider,blocknumber):
    block = httpProvider.eth.getBlock(blocknumber,True)
    
    return block

def getTxTraceByHash(chainObj,hash, dump=False):
    '''
    Returns transaction trace, if only the hash is known/available.
    Optional: set dump to True >> writes the trace to disk (in .json)
    '''
    txObj = chainObj.get_transaction(hash)
    txTrace = txObj.trace

    return txTrace


def getTxTraceByBlock(blocknumber, dump=False):
    '''
    For a given block, returns the traces of all submitted transactions.
    Optional: set dump to True >> writes the traces to disk (in .json)
    '''
    pass

def writeTestResult(result, filename, _path, format="json"):
    '''
    Expects a test result object (usually as a dict or array), filename as string, and a PosixPath.
    Dumps the test result in the _path, as a file format
    defined by format( defauls to json)
    '''
    full_name = _path.joinpath(f"{filename}.{format}")
    with open(full_name, 'w') as writeme:
        if format == "json":
            json.dump(result, writeme, indent=4)


# def debugInfo(block_number, block_info=True, prestate=True tx_receipts=True,tx_traces=True):
#     case 
#     pass

