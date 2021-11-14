#!/bin/env python3
#Works on all '.log' files in directory where the script is executed
"""

Created on Thu Oct 31 20:03:09 2021
Last Modified on Sun Nov 14 01:05:09 2021


@author: davidbartsmets

"""

#-------------------------------FILL-IN-THESE-VARIABLES--------------------------------------------
InputFileSuffix="_md" #Put what you want the inputfile name to end on in here excluding '.gjf'
Calcline='# opt freq 6-311+g(d,p) integral=grid=ultrafine pbe1pbe scf=(xqc,novaracc,noincfock) empiricaldispersion=gd3bj'
Specified_Memory='14GB'#Put specified memory including unit ('5GB','2000MB',...) in this string or leave empty ('') for 4GB default
Specified_Cores='4'#Put specified cores ('2','3',...) in this string or leave empty ('') for 4 cores default 
UseAlone=True #executes the function when this script is run, set to False if you want to run the function with another script
PrintConsole=True #print result of every logfile check
#--------------------------------------------------------------------------------------------------

import datetime
import os
import cclib
import numpy as np

def MakeMDGjf(CalculationDetailsLine,GjfFileSuffix,Memory_given='4GB',Cores_given='4',LineUnderCoords='',DebugPrint=False):
    here=os. getcwd()
    if Memory_given=='':
        Memory='4GB'
    else:
        Memory=Memory_given
    if Cores_given=='':
        Cores='4'
    else:
        Cores=Cores_given
    now = datetime.datetime.now()
    log_files = [f for f in os.listdir('.') if f.endswith('.log')]

    for i in range(len(log_files)):
        NewFileSuffix=GjfFileSuffix+".gjf"
        Imput = log_files[i] 
        f=open(Imput)#Opens Logfile and extracts coordinates, charge, and multiplicity
        parser = cclib.io.ccopen(Imput)
        data = parser.parse()
        HasFreqs=True #assume log has freqs
        
        try:
            summed=np.add(data.vibdisps[0], data.atomcoords[-1])#add manual displacement to imag freq
        except:
            HasFreqs=False
            if DebugPrint:
                print('Skipping '+Imput+' because it does not contain frequencies')
                
        try:
            os.mkdir('./MDs')
        except:
            None
            
        if HasFreqs and data.vibfreqs[0]<0:
            outp = open("./MDs/"+Imput[:-4]+NewFileSuffix,'w')#Starts Writing Outputfile
            outp.write('%rwf='+Imput[:-4]+'.rwf \n')
            outp.write("%NoSave \n")
            outp.write('%chk='+Imput[:-4]+'.chk \n')
            outp.write('%nprocshared='+Cores+' \n')
            outp.write('%mem='+Memory+' \n')
            outp.write(CalculationDetailsLine+'\n')
            outp.write('\n'+ Imput[:-4]+NewFileSuffix+' Inputfile made on: '+now.strftime("%Y-%m-%d %H:%M:%S")+' \n')
            outp.write('\n '+str(data.charge)+' '+str(data.mult)+' \n')                
            for i in range(len(data.atomnos)):
                outp.write (str(data.atomnos[i])+' '+"{:f}".format(summed[i][0])+' '+"{:f}".format(summed[i][1])+' '+"{:f}".format(summed[i][2])+'\n')
            outp.write("\n\n\n")
            outp.close
            if DebugPrint:
                print('New inputfile with manual displacement created for '+Imput+' in ./MDs dir')

        elif HasFreqs and data.vibfreqs[0]>0 and DebugPrint:
            print('No imag freq for '+Imput)

            
#Calls function with argumets specified at the beginning of this file;
if UseAlone:
    MakeMDGjf(Calcline,InputFileSuffix,Memory_given=Specified_Memory,Cores_given=Specified_Cores,DebugPrint=PrintConsole)    
