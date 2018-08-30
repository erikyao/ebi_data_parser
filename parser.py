import pandas as pd
import numpy as np
import io
from datetime import datetime

# read two files
df1 = pd.read_csv('CancerG2P_29_8_2018.csv', sep=',')
df2 = pd.read_csv('DDG2P_29_8_2018.csv', sep=',')
frames = [df1, df2]
df = pd.concat(frames)

# identify missing data
df.replace('No gene mim', np.nan, inplace=True)
df.replace('No disease mim', np.nan, inplace=True)

# separate id
df_hgnc_id = df.loc[:,["hgnc id"]] 
hgnc_id = df_hgnc_id.values[:,0]
del df['hgnc id']

# parse and ignore empty data
dt = df.values
props_names = list(df)
nan_tests = pd.isnull(dt)

result_dict={} # intermediate dict construct

for x in range(0, len(dt)):
    dict_gene = {} # for each observation
    
    for y in range(0, len(dt[0])): # of all observations
        if not (nan_tests[x,y]): # of not NaN properties
            if (y==2 or y==3):
                # additional processsing for disease name and mim
                if 'disease' not in dict_gene:
                    dict_gene['disease'] = {}
                dict_gene['disease'][props_names[y]] = dt[x,y]
            elif (y==7 or y==8 or y==11): 
                # additional processing for rgan specificity list , pre symbols, phenotypes
                dict_gene[props_names[y]] = dt[x,y].split(';')
            elif (y==9): 
                # additional processing for pmids (list of integers)
                dict_gene[props_names[y]] = [int(x) for x in dt[x,y].split(';')]
            elif (y==12):
                dict_gene[props_names[y]] = datetime.strptime(dt[x,y], '%Y-%m-%d %H:%M:%S')
            else:
                dict_gene[props_names[y]] = dt[x,y]
    
    if hgnc_id[x] in result_dict:
        list_gene = result_dict[hgnc_id[x]]['gene2phenotype']
        list_gene.append(dict_gene)
        result_dict[hgnc_id[x]]['gene2phenotype'] = list_gene
    else:
        dict_item = {
            "_id": hgnc_id[x],
             "gene2phenotype": [dict_gene]
        }        
        result_dict[hgnc_id[x]] = dict_item
        
result_list = list(result_dict.values())

# save to a file
file = io.open("result_from_script.txt","w",encoding='utf8')
file.write(str(result_list))
file.close()
