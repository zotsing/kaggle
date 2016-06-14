
# coding: utf-8

"""
This code computes the cosine similarity of item pairs. The input data are in TSV format,
Two files are saved: all results (result1.txt) and first 10000 samples (sample_result1.txt).

BY J.Z. May 19, 2016,

Dev environment:

    Python interpreter:
        Python version: 3.5.1 |Anaconda 2.5.0 (32-bit)| (default, Jan 29 2016) 
        [MSC v.1900 32 bit (Intel)]

    Operating system:
        Windows8_OS

    Processor:
        AMD A10-7800 Radeon R7, 12 Computer Cores 4C+8G 3.5 GHZ

This code takes about 125 seconds to run under the above configuration 

This code calls standard python libraries sys and time is for reference:
    sys, time, and math
    
workflow:
(1) Read file by lines 
(2) import data to dict with itemID as primary key and userID as secondary key
(3) import data to dict with userID as primary key and itemID as secondary key
(4) calculate magnitude for each item vector
(5) calculate dot prodct for each unique item pair
(6) convert to cosine similarity 
    The cosine similarity is calculated using (v(A) dot v(B))/(mag(A)*mag(B))
    source: https://en.wikipedia.org/wiki/Cosine_similarity
(7) write to files per instruction
"""

# import libraries
import sys
import time
from math import sqrt


# Get python version and starting time
st_time = time.time()
print('Python version: ' + sys.version)
print('Starting time: ' + str(st_time))
start_time = time.time()


#create dictionary
d_item = dict() # using itemID as primary key to compute magnitude of each item vector
d_user = dict() # using userID as primary key to compute doc product

# read input dataset to dicts, 
with open('dataset.txt') as f: 
    for line in f:
        user,item = line.rstrip('\n').split('\t') #split input by Tab
        if user and item:  # only get complete pairs
            userID = int(user)   
            itemID = int(item)   

            if itemID in d_item:  # dict using itemID as primary key
                if userID in d_item[itemID]:
                    d_item[itemID][userID] += 1
                else:
                    d_item[itemID][userID] = 1
            else:
                d_item[itemID] = {userID:1}
                
                
            if userID in d_user:  #dict using userID as primary key
                if itemID in d_user[userID]:
                    d_user[userID][itemID] += 1
                else:
                    d_user[userID][itemID] = 1
            else:
                d_user[userID] = {itemID:1}


# computing magnitude
for itemID in d_item:
    sum = 0
    for v in d_item[itemID].values():
        sum += v ** 2
    d_item[itemID]['mag'] = sqrt(sum)

    
# computing dot product 
dotProduct = dict()
while d_user:
    userID,item_cnt = d_user.popitem()
    while item_cnt:
        item_l,cnt_l = item_cnt.popitem()
        for item_r in item_cnt:
            item_key = (item_l,item_r)
            if item_l > item_r:     # for each pair, order does not matter
                item_key = (item_r,item_l)
            try:
                dotProduct[item_key] += cnt_l * item_cnt[item_r]
            except KeyError:
                dotProduct[item_key] = cnt_l * item_cnt[item_r]      

                
# converting dot product to similarity using given formular
for key in dotProduct:
    dotProduct[key] /= d_item[key[0]]['mag'] * d_item[key[1]]['mag']
    dotProduct[key] = float("{0:.6f}".format(dotProduct[key])) # formatting
                            
# add self similarity per description
for k in d_item:
    dotProduct[(k,k)] = 1
    
    
key_list = sorted(dotProduct.keys()) # output using sorted key per instruction
# open file for writing sample 
f_sample = open("sample_result1.txt","w")
f_sample.write('(item_id1, item_id2)\t{cosine similarity}\n')

for key in key_list[:10000]:
    f_sample.write('{}\t{}\n'.format(key, dotProduct[key]))
f_sample.close()

# open file for writing all 
f_all = open("result1.txt","w")
f_all.write('(item_id1, item_id2)\t{cosine similarity}\n')
for item in key_list:
    f_all.write('{}\t{}\n'.format(item, dotProduct[item]))
f_all.close()

print('End, running time: {0:.1f} seconds'.format((time.time() - st_time)))
