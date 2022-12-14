import pandas as pd

def opCodes():
    '''
    Loads a pandas dataframe with implemented opcodes vs gas/circuit cost
    '''
    try:
        op = pd.read_csv('CircuitCosts.csv',sep='|')
        op=op.set_index('opcode')
        print(op.head())
        print("dataframe loaded")
    except:
        print("Error while loading dataframe")
        op = None
    return op

def calcTxCosts(circuit,trace,op,df):
    '''
    Returns total block gas/h per transaction and opcode gas/h per transaction. Takes in circuit (EVM,STATE, etc) opcode 
    name (SDIV, MLOAD etc), tx trace and opcodes circuit costs dataframe (need to load the CircuitCosts.csv with pandas)  
    '''
    TxG = sum([pc['gasCost'] for pc in trace]) 
    opCount = len([pc for pc in trace if pc['op'] == op])
    opTxG = int(df.loc[op][f'g{circuit}']*opCount)
    gRatio = opTxG/TxG
    TxH = int(sum([df.loc[pc['op']][f'h{circuit}'] for pc in trace]))
    opTxH = int(df.loc[op][f'h{circuit}']*opCount)
    hRatio = opTxH/TxH
    print(f' txG: {TxG}\n opCount: {opCount}\n opTxG: {opTxG}\n TxH: {TxH}\n opTxH: {opTxH}\n hRatio: {hRatio}\n gRatio: {gRatio}')

    return TxG,opCount,opTxG,TxH,opTxH, hRatio, gRatio