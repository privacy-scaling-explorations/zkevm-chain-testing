from brownie import CheckSdiv, CheckMload
from web3 import Web3
from web3.middleware import geth_poa_middleware
# from commonUtils import loadJson, getProjectDir


# def load_contracts(jsonmap,sc,cid,):
#     '''
#     creates and returns an instance of the selecred (deployed) contract. 
#     '''
#     scaddr = sc.


def sendTx(numOfiterations,contractInstance,owner):
    '''
    Submits a transaction invoking a contract optimized to produce the worst case
    block for circuit under consideration
    '''
    txNotSent = True
    try:
        tx = contractInstance.checkBatchYul(((numOfiterations),),{"from": owner})
        txNotSent = False
    except ValueError as _err:
        tx = None
        print(_err)

    return tx, txNotSent


def loadContract(jsonmap, cid, contract):
    '''
    Returns a smart contract object to call solidity methods out of. 
    Inputs:
        1. jsonmap and cid will are parsed from main scipts locals() and passed in 
        from calling module
        2. contract: str, must match a deployed contract name. Usually it is passed in 
        by calling module, as return of function getScName

        Returns an instance of the contract
    '''
    sc_address = jsonmap[cid][contract][0]
    sc_instance = globals()[contract].at(sc_address)
    print(sc_instance, type(sc_instance))
    return sc_instance

def setupW3Provider(url,testenv="REPLICA", layer=2):
    '''
    Returns a web3 http provider object to allow interaction with blockchain.
    Takes in the rpc endpoint url, the test environment (testenv:string) and 
    layer: integer as arguments 
    '''
    # print(lcl[0]['env']["rpcUrls"][f'{testenv}'"_BASE"]+"l2")
    w3 = Web3(Web3.HTTPProvider(url))
    w3.middleware_onion.inject(geth_poa_middleware, layer=0)
    cid = str(w3.eth.chainId)

    return w3, cid

def getScName(circuit):
    #TODO: Needs extension every time we add an opcode. Make this a json file and read
    # it in instead
    '''
    Derives the contract name to be invoked, based on the worst case scenario 
    (aka parameter circuit:string) under consideration
    '''
    worstCaseOPs = {
        "EVM"  : ("CheckSdiv","SDIV"),
        "STATE": ("CheckMload", "MLOAD")
    }

    return worstCaseOPs[circuit]

    # def getTxTrace(tx):
#     traceDone = False
#     while not traceDone:
#         try:
#             tr = tx.trace
#             traceDone = True
#             print('Tx trace done')
#         except:
#             print("failed to get tx trace")
    
#     return tr

def getBlockNumber(w3provider):
    block = w3provider.eth.blockNumber
    return block