# zkEVM Chain - TestAutomation tools

## Project Setup

1. #### Environment Deployment
```
TA framework consists of two cloud machines hosted in the PSE aws account,in a 
dedicated VPC.
a. A medium sized inexpensive vm that hosts the test code (brownie, a golang 
client to interact with the precompiled contracts and a fuzzer based on go-fuzz)
b. A memory optimized VM that hosts the whole chain compose project. For proof
benchmarking, the VM should have at least 1T of RAM (at least based on the 
current performance, but for worst case block benches, we probably need
around 2T)
```
```
There is a set of jobs configured in Jenkins to help with deploying, configuring 
and maintaining the full test environment.

(***Run the jobs in this order)

1. zkevm-chain_environment
   - Creates a new cloud instance with the selected ec2 Instance Type. The machine 
     will be tagged "zkevm-chain-docker-<jenkins-user-name>".
   - Installs all needed libraries.
   - Installs user public key to allow ssh access.
   - Installs netdata monitor on http://<private-ip>:19999
   
2. zkevm-chain_deploy
   - Checks out the selected zkevm-chain branch.
   - Modifies the l1-genesis adding a banch of test-accounts.
   - Adapts the compose networking settings.
   - Deploys the chain.
   
3. zkEvmChainTesting_deploy
   - Creates a new cloud instance (fixed instance type).
   - Installs user public key to allow ssh access.
   - Installs the go-client and fuzzer.
   - Performs initial chain configuration (dummy prover vs real prover, number of prover replicas etc).
   - Performs a round of eth deposits to make sure accounts have enough eth in l2
   - Installs brownie and deploys the worst-case-block l2 contracts
   
    * 2 and 3 can be used to deploy new versions of zkevm-chain or test code, if the PRUNE 
    option is enabled.
    
    An option to terminate the environment is also available
```
2. #### Initial Provisioning & Maintenance
```
>>> zkevm-chain_deploy
    - Prover: If selected, coordinator will by default send proof-requests for
    all l2 blocks
    - Single_prover: If selected, one prover replica will be deployed. Otherwise,
    defaults to the compose fixed value
    - Unsafe_RPC: allows RPC calls towards coordinator (needed for coordinator config via rpc)

>>> zkEvmChainTesting_deploy
    - Brownie: installs brownie
    - Funds: eth deposits to L2 (rerun at any time)
    - Contracts: deploys l2 contracts for worst-case-blocks  

Use the Prune option in both jobs to deplpoy the latest version of zkevm-chain and/or TA tools release.
Use the state option in both jobs to shutdown/terminate the cloud instance

>>> control_instances_state
    
    Power on/off the test environment (both machines)
```

## Chain Tools
```
1. Calibrate Opcode for worst case block
    For a given circuit, calculates the number of most expensive opcode executions that fit into a Tx, 
    not exceeding the 300k gas allowance. Start from a large number and iterate with step=-1000 until 
    the Tx does not revert. Returns the number of opcode executions that satisfies the worst case scenario
    per circuit.
    
    Input: loop start value, defaults to 100000
    Dependency: SC for the selected opcode must be deployed

2. eth.blockNumber
    Returns the latest blocknumber 
    Input: Layer (1 or 2)
    
3. get prover tasks
    Audits the prover service for the state of queued/ongoing/finsihed proof tasks.
    If block=0, returns two booleans, indicating proverIdle vs proverBusy and an array
    with the proof tasks results (for exaple output might be (True,False ['ok','ok','Err','None']))
    ('None' indicates a proof task in progress)
    
    If block is specifided !=0, job returns the actual task status/proof result
    
4. get_block_fixtures
    For a selected block, it fetches:
        - block info
        - block pre-state
        - block hashes  
    and saves the generated json files in the job workspace (naming is bloc_fixtures_<blocknumber><username>.tar.gz)
    
5. proof-request
    start a proof task for a given block
    Inputs:
        - block number
        - circuit (pi,super,evm,state,tx,bytecode,copy,exp,keccak)
        - aggregate (bool)
        - retry (bool) If there is a cached task for a given block, repeats the proof generation. If False, task result is returned
        - mock_prover (bool) Select to engage the mock prover
        - mock_prover_if_error (bool) Select to engage the mock prover in case the task fails

[WIP]
- restart chain (resets the compose project to modified genesis. docker volumes are pruned so no state is saved
prover tasks, account balances etc)
- flush prover: remove tasks from prover cache (not the ongoing ones)
- dump Tx trace: select a block (or specific Tx) to collect the trace(s). Will be saved in job workspace
- coordinator config

[TO DO]
- collect prover/mock prover logs
- send logs/fixtures traces to S3 
```
## Proof Benchmarking
```
1. bench-worst-case-300k-gas [WIP]

    Initiates a proof request for a block optimized for maximum h/g. Optimization is done per circuit. 
    To generate the Tx, uses the maximum number of opcode executions that fit into 300k gas, as calculated
    by the calibration step.
    Inputs: 
        - circuit to optimize against
        - proof request options (aggregate, circuit, retry, mock, mock_if_error)
    
    Returns proof result, indicating proof generation duration for circuit and aggregate, selected k, block gas  
    
2. bench-worst-case-custom
    
    Similar to 1, but allows a custom number of opcode executions. Has the same inputs, plus the number of opcode executions.
 
3. prove-simple-Tx-(eth-transfer) [WIP]

    Submits a simple eth transfer Tx and initiates the proof generation for the subsequent block.
    
```
