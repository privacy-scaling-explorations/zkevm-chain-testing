import pandas as pd
import datetime, sys, psycopg2
from pprint import pprint
import json
from sqlalchemy import create_engine

def prepare_wcresult_dataframe(wc_circuit,po_circuit,gas_used,metrics,commit_chain,commit_circuits,dummy=False):
    try:
        if metrics['result'] == 'PASSED':
            result = {
                'wc_circuit'            : wc_circuit,
                'circuit'               : po_circuit,
                'chain_commit_hash'     : commit_chain,
                'circuit_commit_hash'   : commit_circuits,
                'test_date'             : datetime.datetime.now().date(),  
                'duration_circuit'      : str(pd.to_timedelta(metrics["Duration"]["Circuit"],unit='ms')),
                'duration_aggregate'    : str(pd.to_timedelta(metrics["Duration"]["Aggregation"],unit='ms')),
                'degree_circuit'        : metrics["k"]["Circuit"],
                'degree_aggregation'    : metrics["k"]["Aggregation"],
                'gas_used'              : gas_used,
                'dummy'                 : dummy,
                'max_ram'               : "NotImplemented"                
            }
        else:
            result = {
                'wc_circuit'            : wc_circuit,
                'circuit'               : po_circuit,
                'chain_commit_hash'     : commit_chain,
                'circuit_commit_hash'   : commit_circuits,
                'test_date'             : datetime.datetime.now().date(),  
                'duration_circuit'      : 'None',
                'duration_aggregate'    : 'None',
                'degree_circuit'        : 0,
                'degree_aggregation'    : 0,
                'gas_used'              : gas_used,
                'dummy'                 : dummy,
                'max_ram'               : "NotImplemented"
            }
            
    except Exception as e:
        print(e)

    result = pd.DataFrame([result])
    result = result.set_index('test_date')    
    return result


def prepare_integrationresult_dataframe(logs, s3, circuit,metrics, commit_chain,commit_circuits,dummy=False):
    try:
        if metrics['result'] == 'PASSED':
            result = {
                'circuit'               : circuit,
                'chain_commit_hash'     : commit_chain,
                'circuit_commit_hash'   : commit_circuits,
                'test_date'             : datetime.datetime.now().date(),  
                'result'                : metrics["result"],
                'error'                 : 'None',
                'logsurl'               : 'None',
                'dummy'                 : dummy,
                'max_ram'               : "NotImplemented"
            }
        else:
            result = {
                'circuit'               : circuit,
                'chain_commit_hash'     : commit_chain,
                'circuit_commit_hash'   : commit_circuits,
                'test_date'             : datetime.datetime.now().date(),  
                'result'                : metrics["result"],
                'error'                 : metrics["error"],
                'logsurl'               : f"{s3}{logs}",
                'dummy'                 : dummy,
                'max_ram'               : "NotImplemented"
            }
    except Exception as e:
        print(e) 
              
    result = pd.DataFrame([result])
    result = result.set_index('test_date')
    
    return result

def pgsql_engine(pgsqldb):
    user     = pgsqldb['user']
    password = pgsqldb['password']
    host     = pgsqldb['host']
    database = pgsqldb['database']
    engine   = create_engine(f'postgresql://{user}:{password}@{host}:5432/{database}')

    return engine
