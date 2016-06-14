#import libraries
import datetime
import time
from heapq import nlargest
from operator import itemgetter
from collections import defaultdict
import gzip

##find missing values
startT = time.time()
mis_tr = defaultdict(int)
with gzip.open('train.csv.gz','rt') as f:
    title=f.readline().rstrip('\n').split(",")
    for line in f:
        list = line.rstrip('\n').split(",")
        for idx, value in enumerate(list):
            if not value:
                mis_tr[title[idx]] += 1                      
print("time spent {}".format(time.time()-startT))

mis_te = defaultdict(int)
with open('test.csv','r') as f:
    title=f.readline().rstrip('\n').split(",")
    for line in f:
        list = line.rstrip('\n').split(",")
        for idx, value in enumerate(list):
            if not value:
                mis_te[title[idx]] += 1
print("time spent {}".format(time.time()-startT))  
print(mis_tr,mis_te)
