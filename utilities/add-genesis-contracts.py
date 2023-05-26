import json
from pathlib import Path    
import sys
from pprint import pprint

genesis_contracts_dir = sys.argv[2]
chain_dir = sys.argv[1]
EXTCODESIZE_ADDRESS_INT = 500001
BCLENGTH_TARGETS_START_ADDRESS_INT = 600001
SAMPLE_ADDRESS_INT = 100001

l2_genesis = json.load(open(f'{chain_dir}/docker/geth/templates/l2-testnet.json'))
#ADD EXTCODESIZE FOR BYTECODE/KECCAK WC BLOCK
contract = json.load(open(f'{genesis_contracts_dir}/EXTCODESIZE_BYTECODE.json'))
bytecode = f'0x{contract["object"]}'
address = f'0x{EXTCODESIZE_ADDRESS_INT:040d}'
l2_genesis['alloc'][address] = {
        'comment': 'TEST EXTCODESIZE FOR BYTECODE/KECCAK WC BLOCK',
        'balance': '0',
        'code': bytecode
    }
pprint(l2_genesis['alloc'][address])

#ADD TARGET CONTRACTS FOR BC LENGTH CALCULATIONS
TARGET_CONTRACTS=1000
SAMPLE_BC = l2_genesis['alloc'][f'{SAMPLE_ADDRESS_INT:040d}']['code']
for i in range(1,TARGET_CONTRACTS+1):
    address_step = 100*i
    address_int = BCLENGTH_TARGETS_START_ADDRESS_INT + address_step
    A = f'{address_int:040d}'
    BC = hex(int(SAMPLE_BC, 16) + address_step)
    l2_genesis['alloc'][A] = {
        'comment': f'BC LENGTH CALC TARGET {i}',
        'balance': '0',
        'code': BC
        }


with open('l2-testnet.json', 'w') as writeme:
    json.dump(l2_genesis, writeme, indent=4)
