# -*- coding: utf-8 -*-
"""
Created on Fri Dec  5 11:36:19 2014

@author: zhaobin
"""
'plot max,min,mean of all turtles` temperature '
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from turtleModule import str2ndlist
###############################################################
obsData=pd.read_csv('ctdwithoutbad_roms.csv', index_col=0)   
obsturtle_id=pd.Series(obsData['PTT'],index=obsData.index)
obsturtle_ids=obsturtle_id.unique()
length=len(obsturtle_ids)                #length is number of turtles 

ids=[]
for i in range(length):
    ids.append([])   
for i in range(length):
    for j in obsData.index:
        if obsturtle_id[j]==obsturtle_ids[i]:
            ids[i].append(j)                 #collect each turtle`s index
obsmins=[]
obsmaxs=[]
obsmeans=[]
modmins=[]
modmaxs=[]
modmeans=[]                        # collect min,max and mean of model and observe temperature
for i in range(len(ids)):
    obsdata=obsData.ix[ids[i]] 
    goodobstemp=pd.Series(str2ndlist(obsdata['TEMP_VALS']), index=ids[i])
    goodmodtemp=pd.Series(str2ndlist(obsdata['modTempByDepth'],bracket=True), index=ids[i]) #each turtle`s modtemp and obstemp
    obsmin=[]
    obsmax=[]
    obsmean=[]
    modmin=[]
    modmax=[]
    modmean=[]                         
    for j in ids[i]:
        obsmin.append(np.min(np.array(goodobstemp[j]))),modmin.append(np.min(np.array(goodmodtemp[j])))
        obsmax.append(np.max(np.array(goodobstemp[j]))),modmax.append(np.max(np.array(goodmodtemp[j])))
        obsmean.append(np.mean(np.array(goodobstemp[j]))),modmean.append(np.mean(np.array(goodmodtemp[j]))) 
                                                    #each turtle in one location`s max,min,mean temperature
    obsmins.append(np.min(np.array(obsmin)))
    obsmaxs.append(np.max(np.array(obsmax)))
    obsmeans.append(np.mean(np.array(obsmean)))
    modmins.append(np.min(np.array(modmin)))
    modmaxs.append(np.max(np.array(modmax)))
    modmeans.append(np.mean(np.array(modmean)))    #each turtle`s max,min,mean modtemp and obstemp
obsmins.sort()
obsmaxs.sort()
obsmeans.sort()
modmins.sort()
modmaxs.sort()
modmeans.sort()
data=np.round([obsmins,obsmaxs,obsmeans,modmins,modmaxs,modmeans],0)
data_str=['Observe_min','Observe_max','Observe_mean','Model_min','Model_max','Model_mean']  #use for loop

for i in range(len(data)):
    fig=plt.figure()
    y=pd.Series(data[i])
    y1=y.value_counts()
    y1=y1.sort_index()
    plt.bar(y.unique(),y1)
    if i==3:
        plt.xlim([0,25])   #one data in modmins is smaller than 0
    plt.xlabel('Temperature ',fontsize=20)
    plt.ylabel('Quantity',fontsize=20)
    plt.ylim([0,max(y1)+2])
    plt.title(data_str[i],fontsize=20)
    plt.savefig('bar'+data_str[i]+'.png')
plt.show()
