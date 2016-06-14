# import library
from datetime import datetime
import gzip
from operator import itemgetter
from collections import defaultdict
from math import log,ceil,floor
startT = datetime.now()

def hotel_cty_ori_des_markt():
    cty_ori_des_mrkt = defaultdict(lambda: defaultdict(int)) #
    total = 0
    with gzip.open('train.csv.gz','rt') as f:
        tilte = f.readline()
        for line in f:
            
            total += 1
            if total % 8000000 == 0:
                print ('Processed {} rows'.format(total))
                
            lst = line.rstrip('\n').split(",")
            cnty = lst[3]
            cty = lst[5]
            ori_des = lst[6]
            srch_mrkt = lst[22]
            htl_clst = lst[23]
            
            if not ori_des:
                continue
                                    
            if (cnty and cty and ori_des and srch_mrkt and htl_clst):
                cty_ori_des_mrkt[(cnty,cty,ori_des,srch_mrkt)][htl_clst] = 1 #
    return cty_ori_des_mrkt

def write_id(raw_f,pre_dict):
    total = 0
    fw = open("missingID.csv","w")
    fw.write("missingID\n")
    with open(raw_f,'r') as f:
        tilte = f.readline()
        
        for line in f:
            total += 1
            if total % 8000000 == 0:
                print ('Processed {} rows'.format(total))
                
            lst = line.rstrip('\n').split(",")
            cnty = lst[4]
            cty = lst[6]
            ori_des = lst[7]
            srch_mrkt = lst[21]
            id = lst[0]
            
            if not ori_des:
                continue              
                                   
            key1 = (cnty,cty,ori_des,srch_mrkt)
            if cnty and cty and ori_des and srch_mrkt and (key1 in pre_dict):
                 fw.write("{}\n".format(id))     # id and clusters
    fw.close()

if __name__ =='__main__':
    cty_ori_des_mrkt = hotel_cty_ori_des_markt()
    write_id('test.csv',cty_ori_des_mrkt)
    del cty_ori_des_mrkt
