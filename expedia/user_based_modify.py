
# coding: utf-8

from heapq import nlargest
from operator import itemgetter
from collections import defaultdict
import math
import gzip
import numpy as np


def prepare_arrays_match(kdx,ssn,f_tm,f_bk):
    f = gzip.open("train.csv.gz", "rt")
    f.readline()
    hotels_uid_dest_cnty = dict()
    total = 0   
    while 1:
        total += 1
        if total % 8000000 == 0:
            print ('Processed {} rows'.format(total))
        
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
            
        if book_month not in ssn or book_year<2012 or book_year>2015:
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
                
        keys.append((user_id,hotel_country))
        keys.append((user_location_city,srch_destination_id,hotel_market,hotel_country))
 
        keys.append((user_id, hotel_market, hotel_country))
        keys.append((user_id, srch_destination_id, hotel_country))
        keys.append((user_id, srch_destination_id, hotel_country, hotel_market))
        
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


def test_R(kdx,ssn,skipID,raw_f,pre_dict):
    total = 0
    newT = defaultdict(list)
    with open(raw_f,'r') as f:
        tilte = f.readline()
        
        for line in f:
            total += 1
            if total % 4000000 == 0:
                print ('Processed {} rows'.format(total))
                
            arr = line.rstrip('\n').split(",")
            id = int(arr[0])
            user_location_city = arr[6]
            orig_destination_distance = arr[7]
            user_id = arr[8]
            is_package = arr[10]
            srch_destination_id = arr[17]
            hotel_country = arr[20]
            hotel_market = arr[21]
            dtime     = arr[1]
            srch_ci   = arr[12]
            
            if id in skipID:
                continue
                
            if srch_ci:
                book_year = int(arr[12][:4])
                book_month = int(arr[12][5:7])
            else:
                book_year = int(arr[1][:4])
                book_month = int(arr[1][5:7])
            
            if book_month not in ssn: 
                continue 
                
            keys = []    
            keys.append((user_id,hotel_country))
            keys.append((user_location_city,srch_destination_id,hotel_market,hotel_country))
            
            keys.append((user_id, hotel_market, hotel_country))
            keys.append((user_id, srch_destination_id, hotel_country))
            keys.append((user_id, srch_destination_id, hotel_country, hotel_market))
            
            s00 = keys[kdx]
            if s00 in pre_dict and (id not in skipID):
                srch = pre_dict[s00]
                top5 = sorted(srch.items(),key=itemgetter(1),reverse= True)[:5]
                for i in range(len(top5)):
                    newT[id].append(top5[i][0])     # id and clusters
            del keys
    return newT


def rst_update(newT,indx):
    newf = open("submission_" + str(indx+1) + ".csv","w")
    with open("submission_" + str(indx) + ".csv","r") as ftr:
        title = ftr.readline()
        newf.write(title)
        for line in ftr:
            lst = line.rstrip('\n').split(',')
            u_id = int(lst[0].strip())
            
            topF_line = lst[1].lstrip(' ').rstrip(' ').split(' ')
            topF = [int(item) for item in topF_line]
            if u_id in newT and len(newT[u_id]):
                for v in range(len(newT[u_id])):
                    if newT[u_id][v] not in topF:
                        topF.insert(v,newT[u_id][v])  #update 
                        topF.pop()                  # delete ending, keep 5 elements
                    elif newT[u_id][v] != topF[v]:
                        topF.remove(newT[u_id][v])
                        topF.insert(v,newT[u_id][v])
            #print(topF)
            topF_line = [str(item) for item in topF]
            newf.write('{},{}\n'.format(u_id,' '.join(topF_line)))
    newf.close()


startT = datetime.now()
#get ids that need to skip for update
skipID = set()
with open('matching_orig_dest.csv') as f:
    f.readline()
    for line in f:
        num = int(line)
        skipID.add(num)


four_ssn = [[3,4,5],[6,7,8],[9,10,11],[12,1,2]]
for kdx in [0,1,2,3]:
    for sdx,ssn in enumerate(four_ssn):
        indx = sdx + kdx * len(four_ssn)
        print('This is the {} update'.format(indx))
        pre_dict = prepare_arrays_match(kdx,ssn,-0.25,15)
        newT = test_R(kdx,ssn,skipID,'test.csv',pre_dict)
        rst_update(newT,indx)
        del pre_dict
        del newT
        print('Time processed {}'.format(datetime.now()-startT))

