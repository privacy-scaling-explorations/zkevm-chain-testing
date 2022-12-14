import json
from pathlib import Path    
import sys

test_accounts = json.load(open(sys.argv[1]))
genesis = json.load(open(sys.argv[2]))

taccs =  test_accounts.keys()

for account in taccs:
    genesis['alloc'][account] = test_accounts[account]

with open('l1-testnet.json', 'w') as writeme:
    json.dump(genesis, writeme, indent=4) 
