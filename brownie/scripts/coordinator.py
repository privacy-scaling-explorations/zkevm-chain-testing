from scripts.rpcUtils import rpcCall
from pprint import pprint


def fetch_coordinator_config(coordinator_url, params):
    '''
    Returns full coordinator config struct via json rpc call if params=[]
    Otherwise sets the coordinator configuration. See method tools.set_config
    '''
    # data = f'{{"jsonrpc":"2.0","id": 1, "method": "config", "params":[{{}}]}}'
    data = f'{{"jsonrpc":"2.0","id": 1, "method": "config", "params":{params}}}'
    url = coordinator_url
    response = rpcCall(url,data)
    return response