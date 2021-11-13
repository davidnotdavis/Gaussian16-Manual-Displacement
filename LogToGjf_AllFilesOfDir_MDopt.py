#!/bin/env python3
#Works on all '.log' files in directory where the script is executed
"""

Created on Thu Oct 31 20:03:09 2021
Last Modified on Thu Oct 31 20:03:09 2021


@author: davidbartsmets

"""
#To do: copy imag so there is a record
#-------------------------------FILL-IN-THESE-VARIABLES--------------------------------------------
InputFileSuffix="_md"#Put what you want the inputfile name to end on in here excluding '.gjf'
Calcline='# opt freq 6-311+g(d,p) integral=grid=ultrafine pbe1pbe scf=(xqc,novaracc,noincfock) empiricaldispersion=gd3bj'
Specified_Memory='14GB'#Put specified memory including unit ('5GB','2000MB',...) in this string or leave empty ('') for 4GB default
Specified_Cores='4'#Put specified cores ('2','3',...) in this string or leave empty ('') for 4 cores default 
UseAlone=True #executes the function when this script is run, set to False if you want to run the function with another scr#testline: #p cam-b3lyp/6-311+g(d,p) cphf=rdfreq polar(dcshg) scf=(xqc,novaracc,noincfock)ipt
Filter=''
#--------------------------------------------------------------------------------------------------

import datetime
import os
import cclib
import numpy as np
import subprocess

def MakeGjf(CalculationDetailsLine,GjfFileSuffix,Memory_given='4GB',Cores_given='4',LineUnderCoords='',DebugPrint=False):
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

        Imput = log_files[i] #
        try:
            os.mkdir('../ImagLogs')
        except:
            None
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
        if HasFreqs and data.vibfreqs[0]<0 and (not Runningyet(Imput[:-4]+NewFileSuffix)):
            os.system('cp '+Imput+' ../ImagLogs/'+Imput)#ImagLogs/ 
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
            os.chdir("./MDs/")
            os.system('DFTBA_here '+Imput[:-4]+NewFileSuffix+' '+'11:00')
            os.system('python3 WaitForMD.py -i '+Imput[:-4]+NewFileSuffix+' &')
            os.chdir("..")
        elif HasFreqs and data.vibfreqs[0]>0 and DebugPrint:
            print('No imag freq for '+Imput)
        elif Runningyet(Imput[:-4]+NewFileSuffix):
            print('Already running MD calc: '+Imput[:-4]+NewFileSuffix)

def Runningyet(calculation):
    qsta = str(subprocess.check_output(['qsta'])).split('\\n')
    for i in range(len(qsta)-1):
        if qsta[i].split()[4]==calculation:
            if qsta[i].split()[2]=="R":
                return True
    return False
 
#Calls function with argumets specified at the beginning of this file; feel free to get rid of these and 

if UseAlone:
    MakeGjf(Calcline,InputFileSuffix,Memory_given=Specified_Memory,Cores_given=Specified_Cores)    

