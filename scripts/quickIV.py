# -*- coding: utf-8 -*-
"""
Created on Sun Jul 31 23:27:00 2022

@author: darro
"""

import numpy as np
import matplotlib.pyplot as plt
import os
import init

# The default data class
# Contains data from the XY stage and the electrometer
class load_data:
    def __init__(self, loc, fname):
        self.data = np.genfromtxt(os.path.join(loc,fname), delimiter = ',', comments='#', names = True, skip_header=2)
        self.I, self.Is, self.V, self.Vs = {},{},{},{}

# Plotting the IV curve at the breakdown voltage, and the forward threshold
def ivplots():
    figure, axis = plt.subplots(2,1,dpi=200,figsize=(12,12))
    for ch in channels: # Cycle through all sipm channels
        # Plot the breakdown voltage
        axis[0].errorbar(ivr.V['%s'%ch],ivr.I['%s'%ch],xerr=ivr.Vs['%s'%ch],yerr=ivr.Is['%s'%ch],label='SiPM %s'%ch)  
        axis[1].errorbar(ivr.V['%s'%ch],np.abs(ivr.I['%s'%ch]),xerr=ivr.Vs['%s'%ch],yerr=ivr.Is['%s'%ch],label='SiPM %s'%ch)  
        for ax in axis:
            ax.set_xlabel('Reverse Bias [V]')
            ax.set_ylabel('Dark Current [A]')
            ax.legend()
            for item in ([ax.title, ax.xaxis.label, ax.yaxis.label] + ax.get_xticklabels() + ax.get_yticklabels()):
                item.set_fontsize(20)
        axis[1].set_yscale('log')
    figure.tight_layout()
    
def thplots():
    figure, axis = plt.subplots(2,1,dpi=200,figsize=(12,12))
    for ch in channels: # Cycle through all sipm channels
        # Plot the forward threshold bias
        axis[0].errorbar(ivrth.V['%s'%ch],ivrth.I['%s'%ch],xerr=ivrth.Vs['%s'%ch],yerr=ivrth.Is['%s'%ch],label='SiPM %s'%ch)   
        axis[1].errorbar(ivfth.V['%s'%ch],ivfth.I['%s'%ch],xerr=ivfth.Vs['%s'%ch],yerr=ivfth.Is['%s'%ch],label='SiPM %s'%ch)    
        for ax in axis:
            ax.set_xlabel('Reverse Bias [V]')
            ax.set_ylabel('Current [A]')
            ax.legend()
            for item in ([ax.title, ax.xaxis.label, ax.yaxis.label] + ax.get_xticklabels() + ax.get_yticklabels()):
                item.set_fontsize(20)
    figure.tight_layout()

# The data is unaveraged; average the data for repeated measurements
def average(ivtype):
    cols = len(ivtype.data.dtype.names) # What are all the different headers in the data file
    for col in range(cols):
        for ch in channels:
            if ivtype.data.dtype.names[col][:2] == 'Is': # Check if the header is a current measurement
                if ivtype.data.dtype.names[col][5:-2] == '%s'%ch: # Check if the channel is the channel of interest
                    ivtype.I['%s'%ch] = [];ivtype.Is['%s'%ch] = [];ivtype.V['%s'%ch] = [];ivtype.Vs['%s'%ch] = [] # Create dictionaries to hold the averaged data from each channel              
                    #print(ch)
                    vset = [] # Create the list to hold the unique voltage values measured
                    msmts = len(ivtype.data['HV_set_V']) # How many total measurements were done for each channel
                    for i in range(msmts):
                        if not vset: # If the list is empty, add the first voltage value that was measured
                            vset.append(ivtype.data['HV_set_V'][i])
                        if ivtype.data['HV_set_V'][i] != vset[-1]: # If the new voltage value is different than the last value in vset, add the new value to vset
                            vset.append(ivtype.data['HV_set_V'][i])
                    #print(vset)
                    for v in vset: # Loop over the unique voltage values
                        rows = [] # Create a temporary list to hold the values measured at each unique voltage
                        for i in range(msmts): # Iterate over the rows for a channel
                            if ivtype.data['HV_set_V'][i] == v: # Group measurements from the data file according to their unique voltage value
                                rows.append([ivtype.data['VsCH_%i_V'%ch][i],ivtype.data['IsCH_%i_A'%ch][i]]) # Add the measurements from each unique voltage to a temporary list
                        rows = np.array(rows)
                        ivtype.V['%s'%ch].append(np.mean(rows[:,0])) # Average the measurements
                        ivtype.Vs['%s'%ch].append(np.std(rows[:,0])) # Get the standard deviation
                        ivtype.I['%s'%ch].append(np.mean(rows[:,1]))
                        ivtype.Is['%s'%ch].append(np.std(rows[:,1]))
                    
if __name__ == "__main__":
    SCRIPTS,HOME,DATA,ARCHIVE,TEMP,DEV,PROC,PLOTS,REPORTS = init.envr() # Setup the local environment
    
    channels = [1,3,6,7,8,9,10,11,12,14,15,16] # These are the channels that were measured
    #channels.remove(1)
    #channels.remove(3)
    IVs = [] # Create a list to hold the types of measurements done
    # Load the data according to the measurement type
    for i in range(len(os.listdir(DEV))):
        fname = os.listdir(DEV)[i]
        if fname[11:-9] == 'ivfth':
            ivfth = load_data(DEV,fname) # Create the data class
            IVs.append(ivfth)
        if fname[11:-9] == 'ivrth':
            ivrth = load_data(DEV,fname) # Create the data class
            IVs.append(ivrth)
        if fname[11:-9] == 'ivr':
            ivr = load_data(DEV,fname) # Create the data class
            IVs.append(ivr)
    for ivtype in IVs:
        average(ivtype) # Average the data
    ivplots() # Plot the data
    thplots()
