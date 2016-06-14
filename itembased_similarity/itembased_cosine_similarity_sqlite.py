# coding: utf-8

"""
This code computes the cosine similarity of item pairs. The input data are in TSV format,
Two files are saved: all results (result.txt) and first 10000 samples (sample_result.txt).

BY J.Z. May 17, 2016,

Dev environment:

    Python interpreter:
        3.5.1 |Anaconda 2.5.0 (64-bit)| (default, Dec  7 2015, 11:16:01) 
        [GCC 4.4.7 20120313 (Red Hat 4.4.7-1)]

    Operating system:
        CentOS Linux release 7.2.1511 (Core)

    CPU:
        Intel(R) Core(TM) i5 CPU 650 @ 3.20GHz (total of 4 processors)

This code takes about 120 seconds to run under the above configuration 

This code calls four standard python libraries:
    sys, time, sqlite3, and math
    
workflow:
(1) Read file by lines -->
(2) import into sqlite3 database -->
(3) sql grouping and aggregation -->
(4) export sql output, computing cosine similarity -->
(5) write to a new TSV file

The cosine similarity is calculated using (v(A) dot v(B))/(mag(A)*mag(B))
source: https://en.wikipedia.org/wiki/Cosine_similarity

"""

# import libraries
import sys
import time
import sqlite3 as sql
from math import sqrt


# Get python version and starting time
st_time = time.time()
print('Python version: ' + sys.version)
print('Starting time: ' + str(st_time))

# create database
conn = sql.connect('similarity.db')
# create cursor object
cur = conn.cursor()
# create table to store given input dataset
cur.execute("CREATE TABLE IF NOT EXISTS similar(user INT, item INT,count INT);")

# read input dataset to list 
with open('dataset.txt') as f:
    data=[]
    for line in f:
        x,y = line.rstrip('\n').split('\t') #split input by Tab
        if x and y:                         #only append complete rows
            data.append([int(x),int(y)])

# insert list data to database table
cur.executemany("INSERT INTO similar (user,item,count) VALUES (?,?,1);",data)

#save changes 
conn.commit()

""" Create temporary tables to store:
    1. the total occurence count for every (item,user) pair
    2. dot prodct of any two-item pair
    3. squred magnitude of each item
"""
cur.executescript("""
            CREATE TEMPORARY TABLE IF NOT EXISTS grouped AS 
                 SELECT item,user,sum(count) as cnt
                 FROM similar 
                 GROUP BY item,user;
                 
            CREATE TEMPORARY TABLE IF NOT EXISTS dotG AS 
                SELECT t1.item as item1, t2.item as item2,
                sum(t1.cnt*t2.cnt) as dot_matx
                FROM grouped t1, grouped t2
                WHERE t1.user=t2.user
                GROUP BY item1,item2
                HAVING dot_matx > 0;
                
            CREATE TEMPORARY TABLE IF NOT EXISTS sqG AS 
                SELECT item, sum(cnt*cnt) as sq_mag
                FROM grouped 
                GROUP BY item;
                 """)

#  merge tables, to get both dot prodct and squared magnitude for each unique item pair
#  e.g., here item1_id <= item2_id
cur.execute('''SELECT t1.item1,t1.item2,t1.dot_matx,(t2.sq_mag*t3.sq_mag) as sq_sum
               FROM dotG t1, sqG t2, sqG t3
               WHERE t1.item1 <= t1.item2 and t2.item = t1.item1 and t3.item = t1.item2
               ''')

# open files for writing sample and all result
f_sample = open("sample_result.txt","w")
f_all = open("result.txt","w")

# write the first line per request
f_sample.write('(item_id1, item_id2)\t{cosine similarity}\n')
f_all.write('(item_id1, item_id2)\t{cosine similarity}\n')

# logic operator for close sampling file
isClosed = 0

while True:
    # get 10000 lines output per time from database
    results = cur.fetchmany(10000)
    
    if not results:
        break;
    # loop to read one line per time
    for row in results:     
        # computing cosine similarity and change to the format per request
        cos_sim = float("{0:.6f}".format(row[2]/sqrt(row[3]))) 
        f_all.write('({},{})\t{}\n'.format(row[0],row[1],cos_sim))
        if not isClosed:
            f_sample.write('({},{})\t{}\n'.format(row[0],row[1],cos_sim))
      
    if not isClosed:   # close sample file after first results fetch
        f_sample.close()
        isClosed = 1
    
# close result file        
f_all.close()

#close connection to database
conn.close()

print('End, running time: {0:.1f} seconds'.format((time.time() - st_time)))
