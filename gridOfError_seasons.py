# -*- coding: utf-8 -*-
"""
Created on Mon Nov 17 09:36:54 2014
Divide the whole area into drifferent girds, and plot the number of observation
and error in each grid in different seasons.
@author: zhaobin
"""
from matplotlib.mlab import griddata
import netCDF4
import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.basemap import Basemap
import pandas as pd
from datetime import datetime
from turtleModule import str2ndlist,draw_basemap,np_datetime,whichArea
###################################################################################
criteria =10                    # criteria for error
url = 'http://tds.marine.rutgers.edu:8080/thredds/dodsC/roms/espresso/hidden/2006_da/his?lon_rho[0:1:81][0:1:129],lat_rho[0:1:81][0:1:129],u[0:1:69911][0:1:35][0:1:81][0:1:128],v[0:1:69911][0:1:35][0:1:80][0:1:129]'
data = netCDF4.Dataset(url)
lons, lats = data.variables['lon_rho'], data.variables['lat_rho']

lonA, latA = lons[81][0], lats[81][0] # Vertex of ROMS area.
lonB, latB = lons[81][129], lats[81][129]
lonC, latC = lons[0][129], lats[0][129]
lonD, latD = lons[0][0], lats[0][0]
obsData = pd.read_csv('ctdWithdepthofbottom_roms.csv')
modTemp = pd.Series(str2ndlist(obsData['modTempByDepth'],bracket=True), index=obsData.index) # if str has '[' and ']', bracket should be True
obsTemp = pd.Series(str2ndlist(obsData['TEMP_VALS']), index=obsData.index)
obsDepth = pd.Series(str2ndlist(obsData['TEMP_DBAR']), index=obsData.index)
obsTime = pd.Series(np_datetime(obsData['END_DATE']),index=obsData.index)
depthBottom = pd.Series(obsData['depth_bottom'],index=obsData.index)
for i in obsData.index:
    if depthBottom[i]>200:
        depthBottom[i]=200     #Just a little points are deeper than 200m.Removing them can plot depth betterex)
obsLons, obsLats = obsData['LON'], obsData['LAT']

lon_i = np.linspace(-78,-69,100)
lat_i = np.linspace(33,42,100)
depth_i=griddata(np.array(obsLons),np.array(obsLats),np.array(depthBottom),lon_i,lat_i,interp='linear')
SPRING=[]
SUMMER=[]
FALL=[]
WINTER=[]
YEAR=[]
for i in obsTime.index:
    if 2<obsTime[i].month<6:
        SPRING.append(i)
    if 5<obsTime[i].month<9:
        SUMMER.append(i)
    if 8<obsTime[i].month<12:
        FALL.append(i)
    if 11<obsTime[i].month or obsTime[i].month<3:
        WINTER.append(i)
    YEAR.append(i)    # index of seasons and year
season=['spring','summer','fall','winter','year']
SEASON=[SPRING,SUMMER,FALL,WINTER,YEAR]
for k in range(len(season)):
    modNearestIndex = pd.Series(str2ndlist(obsData['modNearestIndex'][SEASON[k]], bracket=True), index=SEASON[k]) # if str has '[' and ']', bracket should be True
    modTemp = pd.Series(str2ndlist(obsData['modTempByDepth'][SEASON[k]],bracket=True), index=SEASON[k])
    obsLon, obsLat = obsData['LON'][SEASON[k]], obsData['LAT'][SEASON[k]]
    obsTime = pd.Series(np_datetime(obsData['END_DATE'][SEASON[k]]), index=SEASON[k])
    obsTemp = pd.Series(str2ndlist(obsData['TEMP_VALS'][SEASON[k]]), index=SEASON[k])
    obsDepth = pd.Series(str2ndlist(obsData['TEMP_DBAR'][SEASON[k]]), index=SEASON[k])
    modLayer = pd.Series(str2ndlist(obsData['modDepthLayer'][SEASON[k]], bracket=True), index=SEASON[k])
    data = pd.DataFrame({'lon': obsLon, 'lat': obsLat,
                     'obstemp': obsTemp.values,'modtemp':modTemp,
                     'time': obsTime.values, 'nearestIndex': modNearestIndex.values,
                     'depth':obsDepth,'layer':modLayer},index=SEASON[k])
    lonsize = [np.amin(lons), np.amax(lons)]
    latsize = [np.amin(lats), np.amax(lats)]
    errorNum = []
    for i in range(9):
        j = [0,0,0,0,0,0,0,0,0,0,0,0,0]
        errorNum.append(j)
    fig = plt.figure()
    ax = fig.add_subplot(111)
    draw_basemap(fig, ax, lonsize, latsize)
    plt.plot([lonA, lonB, lonC, lonD, lonA], [latA, latB, latC, latD, latA], 'b-')
    for i in range(0, 75, 10):      # Here use num smller than 81 because the last grid is too small
        plt.plot([lons[i][0], lons[i][129]], [lats[i][0], lats[i][129]], 'b--')
    for i in range(0, 129, 10):
        plt.plot([lons[0][i], lons[81][i]], [lats[0][i], lats[81][i]], 'b--') #plot grid
    r1 = range(0, 81, 10)
    r2 = range(0, 129, 10)
    nearestIndex = []
    '''
    for a in data.index:
        diff = np.array(data['obstemp'][a]) - np.array(data['modtemp'][a])
        indx = np.where(abs(diff)>criteria)[0]
        if not indx.size: continue
        nearestIndex.extend([modNearestIndex[a]] * indx.size)    # calculate all error data
    '''
    for i in data.index:
        if abs(obsDepth[i][-1]-depthBottom[i])<10:     #diff<10m,wo can use the data
            diff = np.array(data['obstemp'][i][-1]) - np.array(data['modtemp'][i][-1])
            indx = np.where(abs(diff)>criteria)[0]
            if not indx.size: continue
            nearestIndex.extend([modNearestIndex[i]] * indx.size)       #calculate error data in bottom
    
    for b in nearestIndex:
        m = whichArea(b[0], r1)
        n = whichArea(b[1], r2)
        errorNum[m][n] += 1      #calculate error data in bottom
    m1, m2 = 34.05, 39.84           # m1, m2 are the location to put Text.
    n1, n2 = -75.83, -67.72         # n1, n2 are the location to put Text.
    for s in range(8):
        a = np.arange(n1, n2, 0.631)
        b = np.arange(m1, m2, 0.47)
        for i, j, q in zip(a, b, errorNum[s]):
            plt.text(i, j, str(q), color='r',multialignment='center')
        m1 = m1 + 0.408
        m2 = m2 + 0.408
        n1 = n1 - 0.45
        n2 = n2 - 0.45
    CS1=plt.contour(lon_i, lat_i,depth_i,1,colors = 'r')
    ax.annotate('100m depth',xy=(-72.0963,38.9144),xytext=(-71.5662,38.8756),arrowprops=dict(facecolor='black'))
    plt.title('Distribution of Error ,'+season[k]+',criteria ='+str(criteria), fontsize=30)
    plt.savefig('gridOfError_'+season[k]+str(1)+'.png')
##########################Plot whole data distribution##########################
    dataNum = []
    for i in range(9):
        j = [0,0,0,0,0,0,0,0,0,0,0,0,0]
        dataNum.append(j)
    fig = plt.figure()
    ax = fig.add_subplot(111)
    draw_basemap(fig, ax, lonsize, latsize)
    plt.plot([lonA, lonB, lonC, lonD, lonA], [latA, latB, latC, latD, latA], 'b-')
    for i in range(0, 75, 10):      # Here use num smller than 81 because the last grid is too small
        plt.plot([lons[i][0], lons[i][129]], [lats[i][0], lats[i][129]], 'b--')
    for i in range(0, 129, 10):
        plt.plot([lons[0][i], lons[81][i]], [lats[0][i], lats[81][i]], 'b--')  #plot grid
    r1 = range(0, 81, 10)
    r2 = range(0, 129, 10)
    nearestIndex = []
    '''   
    for i in data.index:
        m = len(data['obstemp'][i])
        nearestIndex.extend([modNearestIndex[i]] * m)   # calculate all data 
    '''
    for i in data.index:
        if abs(obsDepth[i][-1]-depthBottom[i])<10:     #diff<10m,wo can use the data
            m = len([data['obstemp'][i][-1]])
            nearestIndex.extend([modNearestIndex[i]] * m)   #calculate all data in bottom
    
    for i in nearestIndex:
        m = whichArea(i[0], r1)
        n = whichArea(i[1], r2)
        dataNum[m][n] += 1
    m1, m2 = 34.05, 39.84                # m1, m2 are the location to put Text.
    n1, n2 = -75.83, -67.72              # n1, n2 are the location to put Text.
    for s in range(8):
        a = np.arange(n1, n2, 0.631)
        b = np.arange(m1, m2, 0.47)
        for i, j, q in zip(a, b, dataNum[s]):
            plt.text(i, j, str(q), color='r',multialignment='center', ha='center')
        m1 = m1 + 0.408
        m2 = m2 + 0.408
        n1 = n1 - 0.45
        n2 = n2 - 0.45
    CS1=plt.contour(lon_i, lat_i,depth_i,1,colors = 'r')
    ax.annotate('100m depth',xy=(-72.0963,38.9144),xytext=(-71.5662,38.8756),arrowprops=dict(facecolor='black'))
    plt.title('Distribution of Data ,'+season[k], fontsize=30)
    plt.savefig('gridOfError_'+season[k]+str(2)+'.png')
############################Plot ratio distribution##############################
    ratio = []
    for i in range(9):
        j=[0,0,0,0,0,0,0,0,0,0,0,0,0]
        ratio.append(j)
    fig = plt.figure()
    ax = fig.add_subplot(111)
    draw_basemap(fig, ax, lonsize, latsize)
    plt.plot([lonA, lonB, lonC, lonD, lonA], [latA, latB, latC, latD, latA], 'b-')
    for i in range(0, 75, 10):      # Here use num smller than 81 because the last grid is too small
        plt.plot([lons[i][0], lons[i][129]], [lats[i][0], lats[i][129]], 'b--')
    for i in range(0, 129, 10):
        plt.plot([lons[0][i], lons[81][i]], [lats[0][i], lats[81][i]], 'b--')#plot grid
    r1 = range(0, 81, 10)
    r2 = range(0, 129, 10)
    for i in range(len(errorNum)):
        ratio[i]=(np.array(errorNum[i])/(np.array(dataNum[i])*1.0))*100
    m1, m2 = 34.05, 39.84               # m1, m2 are the location to put Text.
    n1, n2 = -75.83, -67.72             # n1, n2 are the location to put Text.              
    for s in range(8):
        a = np.arange(n1, n2, 0.631)
        b = np.arange(m1, m2, 0.47)
        for i, j, q in zip(a, b, ratio[s]):
            plt.text(i, j, str(round(q,2)), color='r',multialignment='center', ha='center')
        m1 = m1 + 0.408
        m2 = m2 + 0.408
        n1 = n1 - 0.45
        n2 = n2 - 0.45
    CS1=plt.contour(lon_i, lat_i,depth_i,1,colors = 'r')
    ax.annotate('100m depth',xy=(-72.0963,38.9144),xytext=(-71.5662,38.8756),arrowprops=dict(facecolor='black'))
    plt.title('Distribution of Ratio ,'+season[k]+',criteria ='+str(criteria), fontsize=30)
    plt.savefig('gridOfError_'+season[k]+str(3)+'.png')   
plt.show()
