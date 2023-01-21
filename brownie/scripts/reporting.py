import pandas as pd
import datetime, sys, psycopg2
from pprint import pprint
import json
from sqlalchemy import create_engine

def prepare_wcresult_dataframe(test_id, wc_circuit,po_circuit,gas_used,metrics,commit_chain,commit_circuits,dummy=False):
    try:
        if metrics['result'] == 'PASSED':
            result = {
                'test_id'               : test_id,
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
                'max_ram'               : 0
            }
        else:
            result = {
                'test_id'               : test_id,
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
                'max_ram'               : 0
            }

    except Exception as e:
        print(e)

    result = pd.DataFrame([result])
    result = result.set_index('test_date')
    return result


def prepare_integrationresult_dataframe(test_id, logs, s3, circuit,metrics, commit_chain,commit_circuits,dummy=False):
    try:
        if metrics['result'] == 'PASSED':
            result = {
                'test_id'               : test_id,
                'circuit'               : circuit,
                'chain_commit_hash'     : commit_chain,
                'circuit_commit_hash'   : commit_circuits,
                'test_date'             : datetime.datetime.now().date(),
                'duration_circuit'      : str(pd.to_timedelta(metrics["Duration"]["Circuit"],unit='ms')),
                'duration_aggregate'    : str(pd.to_timedelta(metrics["Duration"]["Aggregation"],unit='ms')),
                'degree_circuit'        : metrics["k"]["Circuit"],
                'degree_aggregation'    : metrics["k"]["Aggregation"],
                'result'                : metrics["result"],
                'error'                 : 'None',
                'logsurl'               : 'None',
                'dummy'                 : dummy,
                'max_ram'               : "Not yet"
            }
        else:
            result = {
                'test_id'               : test_id,
                'circuit'               : circuit,
                'chain_commit_hash'     : commit_chain,
                'circuit_commit_hash'   : commit_circuits,
                'test_date'             : datetime.datetime.now().date(),
                'duration_circuit'      : 'None',
                'duration_aggregate'    : 'None',
                'degree_circuit'        : 0,
                'degree_aggregation'    : 0,
                'result'                : metrics["result"],
                'error'                 : str(metrics["error"])[:199],
                'logsurl'               : f"{s3}{logs}",
                'dummy'                 : dummy,
                'max_ram'               : "Not yet"
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

#####################################################
################# REPORTING SYSSTAT #################
#####################################################

def prepare_test_sysstats(statsDir):
    cstats = f'{statsDir}/cpu.stats'
    mstats = f'{statsDir}/mem.stats'
    cpu_stats           = pd.read_csv(cstats)
    cpu_stats.columns   = ('timestamp','CPU','user','nice','system','iowait','steal','idle')
    cpu_stats           = cpu_stats[['timestamp','CPU','idle']]
    cpu_stats['idle']   = pd.to_numeric(cpu_stats['idle'],errors='coerce')
    cpu_stats           = cpu_stats[cpu_stats.CPU != 'CPU']
    cpus                = cpu_stats[cpu_stats['CPU']!='all']['CPU'].unique()
    cpus                = [int(i) for i in cpus if i]

    cpu_all_df = cpu_stats[cpu_stats['CPU'] == 'all']
    cpu_all_Max = float(100) - cpu_all_df['idle'].min()
    cpu_all_Max = round(cpu_all_Max, 2)
    cpu_all_Average = float(100) - cpu_all_df[cpu_all_df['timestamp'] == 'Average'].iloc[0]['idle']
    cpu_all_Average = round(cpu_all_Average, 2)

    mem_stats = pd.read_csv(mstats)
    mem_stats.columns = ('timestamp','kbmemfree','kbavail','kbmemused','%memused','kbbuffers','kbcached','kbcommit','%commit','kbactive','kbinact','kbdirty')
    mem_stats = mem_stats[['kbmemused']]
    absolute = mem_stats['kbmemused']
    mem_stats['absolute'] = absolute
    def s2f(s):
        return float("".join([i for i in s if not i.isalpha()]))
    mem_stats['absolute'] = mem_stats['absolute'].apply(s2f)
    max_idx = mem_stats['absolute'].idxmax()
    max_ram = mem_stats.iloc[max_idx]['kbmemused']

    sysstat = {
        'cpu_all_Average': cpu_all_Average,
        'cpu_all_Max'    : cpu_all_Max,
        'cpu_count'      : len(cpus),
        'max_ram'        : max_ram
    }

    return sysstat, cpu_stats, cpus

def write_test_post_data(engine, grafana_url, test_id, table, statsDir):
    sysstat, cpu_statistics, cpus = prepare_test_sysstats(statsDir)
    # engine = pgsql_engine(pgsqldb)

    cpu_all_Average = sysstat["cpu_all_Average"]
    cpu_all_Max     = sysstat["cpu_all_Max"]
    cpu_count       = sysstat["cpu_count"]
    max_ram         = sysstat["max_ram"]
    cpu_stats       = f"{grafana_url}{test_id}"
    
    sql=( 
        f"UPDATE {table}\n"
        f'SET "cpu_all_Average" = {cpu_all_Average},\n'
        f'"cpu_all_Max" = {cpu_all_Max},\n'
        f'"cpu_count" = {cpu_count},\n'
        f"max_ram = '{max_ram}',\n"
        f"cpu_stats = '{cpu_stats}'\n"
        f"WHERE test_id='{test_id}';"
    )
    
    print(sql)
    
    with engine.begin() as conn:
        conn.execute(sql)

    return cpu_statistics,cpus

######################################################
################# REPORTING PER VCPU #################
######################################################

def write_perCore_stats(engine, cpu_statistics, cpus,test_id,dummy=False):
    # engine = pgsql_engine(pgsqldb)
    cpu_statistics = cpu_statistics[cpu_statistics['CPU'] != 'all']
    cpu_statistics['CPU'] = cpu_statistics['CPU'].astype(int)
    result = pd.DataFrame(columns = ['vCore','vCore_Average','vCore_Max'])
    for cpu in cpus:
        try:
            series = {
                'vCore'         : cpu,
                'vCore_Average' : round(float(100) - cpu_statistics[cpu_statistics['CPU'] == cpu][cpu_statistics['timestamp'] == 'Average'].iloc[0]['idle'], 2),
                'vCore_Max'     : round(float(100) - cpu_statistics[cpu_statistics['timestamp'] != 'Average'][cpu_statistics['CPU'] == cpu]['idle'].min(), 2),
                'dummy'         : dummy,
                'test_id'       : test_id
            }
        except:
            pass
        # print(series)
        result = result.append([series],ignore_index=True)
    
    table='testresults_cpustat'
    result.to_sql(table,engine,if_exists='append',index=False)

