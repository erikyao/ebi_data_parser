import csv
import io
import json
import sys
import os.path
from datetime import datetime

if (len(sys.argv)!=4):
    print ('python parser.py  <input_file1> <input_file2> <output_file>')
    exit(1)    

if not (os.path.exists(sys.argv[1])) or not (os.path.exists(sys.argv[2])):
    print ('At least one file does not exist.')
    exit(1)

f1_name = sys.argv[1]
f2_name = sys.argv[2]
f3_name = sys.argv[3]

def load_data(f1_name, f2_name, f3_name):
    # read two files
    dt1 = list(csv.reader(open(f1_name)))
    dt2 = list(csv.reader(open(f2_name)))

    # clean data
    props_names = dt1[0]
    dt1_header_removed = dt1[1:]
    dt2_header_removed = dt2[1:]

    def cleanCSV(ls):
        for row in ls:
            if (row[1]=='No gene mim'): row[1]=''
            if (row[3]=='No disease mim'): row[3]=''
            
    cleanCSV(dt1_header_removed)
    cleanCSV(dt2_header_removed)

    dt = dt1_header_removed + dt2_header_removed

    # parse and ignore empty data
    from datetime import datetime

    result_dict={} # intermediate dict construct, with unique ids

    for x in range(len(dt)):  # of all observations
        dict_gene = {} # each observation's storage to attach to the 'gene2phenotype' of its unique id in main dict
        
        for y in range(len(dt[0])): # of all properties
            if dt[x][y]!='': # of not empty properties
                if (y==2 or y==3):
                    # additional processsing for disease name and mim
                    if 'disease' not in dict_gene:
                        dict_gene['disease'] = {}
                    dict_gene['disease'][props_names[y]] = dt[x][y]
                elif (y==7 or y==8 or y==11): 
                    # additional processing for rgan specificity list , pre symbols, phenotypes
                    dict_gene[props_names[y]] = dt[x][y].split(';')
                elif (y==9): 
                    # additional processing for pmids (list of integers)
                    dict_gene[props_names[y]] = [int(x) for x in dt[x][y].split(';')]
                elif (y==12):
                    continue
                elif (y==13):
                    dict_gene[props_names[y]] = datetime.strptime(dt[x][y], '%Y-%m-%d %H:%M:%S')
                else:
                    dict_gene[props_names[y]] = dt[x][y]
        
        if int(dt[x][12]) in result_dict:
            list_gene = result_dict[int(dt[x][12])]['gene2phenotype']
            list_gene.append(dict_gene)
            result_dict[int(dt[x][12])]['gene2phenotype'] = list_gene
        else:
            dict_item = {
                "_id": int(dt[x][12]),
                "gene2phenotype": [dict_gene]
            }        
            result_dict[int(dt[x][12])] = dict_item
            
    result_list = list(result_dict.values())

    # save to a file
    file = io.open(f3_name,"w",encoding='utf8')
    file.write(json.dumps(result_list, indent=4, sort_keys=True, default=str))
    file.close()

load_data(f1_name, f2_name, f3_name)