import csv
import io
import json
import sys
import os.path
from datetime import datetime
from biothings.utils.dataload import open_anyfile

def load_data(input_file):
    with open_anyfile(input_file) as in_f:
    
        # read all
        dt = list(csv.reader(in_f))

        # catagorization
        header = dt[0]
        content = dt[1:]

        # remove empty values
        for row in content:
            if (row[1]=='No gene mim'): row[1]=''
            if (row[3]=='No disease mim'): row[3]=''
                
        result_dict={} # intermediate dict construct, with unique ids

        for x in range(len(content)):  # of all observations
            dict_gene = {} # each observation's storage to attach to the 'gene2phenotype' of its unique id in main dict
            
            for y in range(len(content[0])): # of all properties
                if content[x][y]!='': # of not empty properties
                    if (y==2 or y==3):
                        # additional processsing for disease name and mim
                        if 'disease' not in dict_gene:
                            dict_gene['disease'] = {}
                        dict_gene['disease'][header[y]] = content[x][y]
                    elif (y==7 or y==8 or y==11): 
                        # additional processing for rgan specificity list , pre symbols, phenotypes
                        dict_gene[header[y]] = content[x][y].split(';')
                    elif (y==9): 
                        # additional processing for pmids (list of integers)
                        dict_gene[header[y]] = [int(x) for x in content[x][y].split(';')]
                    elif (y==12):
                        # ignore _id here
                        continue
                    elif (y==13):
                        dict_gene[header[y]] = datetime.strptime(content[x][y], '%Y-%m-%d %H:%M:%S')
                    else:
                        dict_gene[header[y]] = content[x][y]
            # _id exists
            if int(content[x][12]) in result_dict:
                list_gene = result_dict[int(content[x][12])]['gene2phenotype']
                list_gene.append(dict_gene)
                result_dict[int(content[x][12])]['gene2phenotype'] = list_gene
            else:
                dict_item = {
                    "_id": int(content[x][12]),
                    "gene2phenotype": [dict_gene]
                }        
                result_dict[int(content[x][12])] = dict_item
                
        return list(result_dict.values())

if __name__ == "__main__":

    if (len(sys.argv)!=3):
        print ('python parser.py  <input_file> <output_file>')
        exit(1)    

    if not (os.path.exists(sys.argv[1])):
        print ('input file does not exist.')
        exit(1)

    f1_name = sys.argv[1]
    f2_name = sys.argv[2]

    result_list = load_data(f1_name)

    # save to a file
    file = io.open(f2_name, "w", encoding='utf8')
    file.write(json.dumps(result_list, indent=4, sort_keys=True, default=str))
    file.close()