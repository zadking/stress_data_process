# -*- coding: utf-8 -*-
"""
Created on Mon Jun 25 10:51:59 2018

@author: zdking
"""

import os
import pandas as pd
import matlab.engine
import csv
import numpy as np
from scipy import stats
import scipy.fftpack
import math
import matplotlib.pyplot as plt

def getfreq(data):
    fourier = scipy.fftpack.fft(data)
    n = data.size
    fourier = abs(data/n)
    freq = scipy.fftpack.fftfreq(n)
    Low = 0
    Med = 0
    Hi = 0
    i = 0
    for val in freq:
        if val >= 0.1 and val < 0.2:
            Low = Low + fourier[i]
        if val >= 0.2 and val < 0.3:
            Med = Med + fourier[i]
        if val >= 0.3 and val < 0.4:
            Hi = Hi + fourier[i]
        i += 1
    return [Low, Med, Hi]

def diff(data):
    i = 0
    flag = 0
    dif  = np.array([])
    for val in data:
         if flag > 0:
             if data[i] > 0:
                 dif = np.append(dif,abs(val-data[i-1]))
             else:
                 flag = -1
         flag += 1        
         i += 1 
    return dif

def calc_fft(y):
    # TEST CASE:
    # >>>print(calc_fft(np.array([1,2,3,4,5,4,3,2,1,2,3,4,5,4,3,2,1,2,3,4,5,4,3]), 16))
    # output:
    # >>>[ 0.10867213  0.22848475  1.67556733  0.1980655   0.11177658  0.08159451
    # 0.07137028  0.12458543  0.26419639  0.10726005]

    # Number of samplepoints
    N = y.shape[0]

    yf = scipy.fftpack.fft(y)
    amp = 2.0/N * np.abs(yf[:int(N/2)])

    return amp

def convert_HR(data):
    HR = np.array([])
    for val in data:
        HR = np.append(HR,(60000/float(val))+1)
    return HR
    
def zerocross(data):
    i = 0
    cnt = 0
    mean = np.mean(data,axis = 0)
    for val in data:
         if i >0:
             if ((data[i] > mean) and (data[i-1] < mean)) or ((data[i] < mean) and (data[i-1] > mean)):
                 cnt += 1
         i += 1 
    return cnt

def getfeatures(data):
     temp = data
     data = data[np.where(data>0)]
     min = np.amin(data,axis = 0)
     max = np.amax(data,axis = 0)
     mean = np.mean(data,axis = 0)
     median = np.median(data,axis =0)
     mode = stats.mode(data, axis = 0)
     sd = np.std(data,axis = 0)
     skew = stats.skew(data,axis = 0)
     kur = stats.kurtosis(data,axis = 0)
     eightper = np.percentile(data, 80,axis = 0)
     sixper = np.percentile(data, 60,axis = 0)
     fourper = np.percentile(data, 40,axis = 0)
     twoper = np.percentile(data, 20,axis = 0)
     rms = np.sqrt(np.mean(data**2))
     iqr = stats.iqr(data,axis = 0)
     countgeq = len(np.where( data > mean)[0])/float(len(data))
     countleq = len(np.where( data < mean)[0])/float(len(data))
     rang = max - min
     [Lf, MF, HF] = getfreq(data)
     COV_M = np.cov(data.T)
     dif = diff(temp)
     pNN50 = len(dif[(np.where(dif>50))])/float(len(data))
     pNN20 = len(dif[(np.where(dif>20))])/float(len(data))
     RMSSD = math.sqrt(np.mean(dif*dif))
     nn50 = len(dif[(np.where(dif>50))])
     nn20 = len(dif[(np.where(dif>20))])
     SDSD =  np.std(dif,axis = 0)
     zcross = zerocross(data)
     #HR = convert_HR(data)
     Count = len(data)
     return [mean,sd,min,max,median,mode,skew,kur,eightper,sixper,fourper,twoper,rms,
             iqr,countgeq,countleq,rang,COV_M,pNN50,pNN20,RMSSD,nn50,nn20,SDSD,zcross, Lf, MF, HF, Lf/HF, Count]
 
eng = matlab.engine.start_matlab()
with open('featurespart101.csv', 'wb') as ec:
    writerec = csv.writer(ec)
    writerec.writerow(['Participant', 'day','window','mean','standar deviation','min','max','median','mode','skew'
                       ,'Kurtosis','80_percentile','60_percentile','40_percentile','20_percentile','RMS'
                       ,'IQR','count>mean','count<mean','range','COV_M','pNN50','pNN20','RMSSD','nn50'
                       ,'nn20','SDSD','zcross', 'Lf', 'MF', 'HF', 'Lf/HF', 'Count'])
    for part in os.listdir('../In_Wild/'):
        print part
        for day in os.listdir('../In_Wild/'+str(part) +'/'):
            ecgfilename = '../In_Wild/'+str(part) +'/' + day + '/elec.csv'
            print day
            ecg = pd.read_csv(ecgfilename)
    #    Timestamp (ms)	Sample (V)
            Time = ecg['Timestamp (ms)']
            start = Time[0]
            endact = Time[len(Time)-1]
            window = 1
            end = start + 60000
            while start <= endact-30000:
                actecg = ecg.loc[(ecg['Timestamp (ms)'] >= start) & (ecg['Timestamp (ms)'] <= end)]
                x = list(actecg['Sample (V)'])
                with open('noise.csv', 'wb') as f:
                    writer = csv.writer(f)
                    for val in x:
                        writer.writerow([val])
                mat_signal = matlab.double(x)[0]
                res = eng.feature_min()
                y = np.array(list(res[0]))
                test = y[np.where(y>0)]
                if len(test) > 10:
                    feat = getfeatures(y)
                    ret = [part,start,window]
                    ret = ret + feat
                    writerec.writerow(ret)
                window += 1
                start = start + 30000
                end = start + 60000
                if end > endact:
                    end = endact
                
                
                
                
        


