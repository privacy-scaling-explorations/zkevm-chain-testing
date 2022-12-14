import requests

def rpcCall(url,data):
    r = requests.post(url,data)
    return r
