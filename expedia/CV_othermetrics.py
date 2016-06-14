
# coding: utf-8

# In[1]:

import datetime
from heapq import nlargest
from operator import itemgetter
import math
import gzip
import numpy as np

#get popularity dicts
def prepare_arrays_match(kdx,ssn,f_tm,f_bk):
    f = gzip.open("train.csv.gz", "rt")
    f.readline()
    hotels_uid_dest_cnty = dict()
       
    while 1:
        line = f.readline().strip()
        
        if line == '':
            break

        arr = line.split(",")
        
        if arr[11] != '':
            book_year = int(arr[11][:4])
            book_month = int(arr[11][5:7])
        else:
            book_year = int(arr[0][:4])
            book_month = int(arr[0][5:7])
            
        if book_month not in ssn or book_year<2012 or book_year>2014:
            continue
            
        append_0 = ((book_year - 2012)*12 + (book_month - 12))
        if not (append_0>0 and append_0<=36):
            continue
                     
        user_location_city = arr[5]
        orig_destination_distance = arr[6]
        user_id = arr[7]
        srch_destination_id = arr[16]
        hotel_country = arr[21]
        hotel_market = arr[22]
        is_booking = int(arr[18])
        hotel_cluster = int(arr[23])
             

        keys = []
        wgt = append_0 * (f_tm + 1) * (1 + is_booking * f_bk)
        keys.append((user_id, srch_destination_id, hotel_country, hotel_market))
        keys.append((user_id, srch_destination_id, hotel_country))
        keys.append((user_id, hotel_market, hotel_country))
        keys.append((user_id,hotel_country))
        keys.append(user_id)
        keys.append((user_location_city,srch_destination_id,hotel_market,hotel_country))
        keys.append((user_location_city,hotel_market,hotel_country))
        keys.append((srch_destination_id,hotel_market,hotel_country))
        keys.append((hotel_market,hotel_country))
        keys.append(hotel_country)
        s00 = keys[kdx]
        if s00 in hotels_uid_dest_cnty:
            if hotel_cluster in hotels_uid_dest_cnty[s00]:
                 hotels_uid_dest_cnty[s00][hotel_cluster] += int(wgt)
            else:
                hotels_uid_dest_cnty[s00][hotel_cluster] = int(wgt)
        else:
             hotels_uid_dest_cnty[s00] = {hotel_cluster:int(wgt)}
        del keys
    f.close()
   
    return hotels_uid_dest_cnty

##evaluation metrics
def gen_eval(kdx,ssn,hotels_uid_dest_cnty):
    scoreBk=[]
    scoreAll=[]
    f = open("cv.csv", "r")
    f.readline()
    ofAll = 0
    ofBk  = 0
    while 1:
        line = f.readline().strip()
        
        if line == '':
            break

        arr = line.split(",")
        
        if arr[11] != '':
            book_year = int(arr[11][:4])
            book_month = int(arr[11][5:7])
        else:
            book_year = int(arr[0][:4])
            book_month = int(arr[0][5:7])
         
        if book_month not in ssn or book_year < 2012:
            continue
            
        user_location_city = arr[5]
        orig_destination_distance = arr[6]
        user_id = arr[7]
        is_package = arr[9]
        srch_destination_id = arr[16]
        hotel_country = arr[21]
        hotel_market = arr[22]
        is_booking = int(arr[18])
        hotel_cluster = int(arr[23])
        append_0 = ((book_year - 2012)*12 + (book_month - 12))
            
        keys = []
        wgt = append_0 * (f_tm + 1) * (1 + is_booking * f_bk)
        keys.append((user_id, srch_destination_id, hotel_country, hotel_market))
        keys.append((user_id, srch_destination_id, hotel_country))
        keys.append((user_id, hotel_market, hotel_country))
        keys.append((user_id,hotel_country))
        keys.append(user_id)
        keys.append((user_location_city,srch_destination_id,hotel_market,hotel_country))
        keys.append((user_location_city,hotel_market,hotel_country))
        keys.append((srch_destination_id,hotel_market,hotel_country))
        keys.append((hotel_market,hotel_country))
        keys.append(hotel_country)
        s00 = keys[kdx]
      
        if s00 in hotels_uid_dest_cnty:
            ofAll += 1
            srch = hotels_uid_dest_cnty[s00]
            top5 = sorted(srch.items(),key=itemgetter(1),reverse= True)[:5]
           
            for i in range(len(top5)):
                if top5[i][0]==hotel_cluster:
                    scoreAll.append(1/(1+i))
                    break              
                                        
            if is_booking:
                ofBk += 1
                for i in range(len(top5)):
                    if top5[i][0]==hotel_cluster:
                        scoreBk.append(1/(1+i))
                        break 
            del keys
    f.close()
    print(sum(scoreAll)/ofAll,len(scoreAll),np.mean(scoreAll),sum(scoreBk)/ofBk,           len(scoreBk),np.mean(scoreBk))
    del scoreBk,scoreAll


#find best parameters
four_ssn = [list(range(1,13)),[12,1,2]]
for idx,ssn in enumerate(four_ssn):
    for f_tm in [-0.5,0,0.5]:
        for f_bk in [0,10,20]:
            for kdx in range(10):
                hotels_uid_dest_cnty = prepare_arrays_match(kdx,ssn, f_tm, f_bk)
                print(kdx)
                gen_eval(kdx,ssn,hotels_uid_dest_cnty)
                del hotels_uid_dest_cnty

