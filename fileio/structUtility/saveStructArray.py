#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr  2 15:09:30 2018

@author: yanglite
"""
from struct2char import *

def saveStructArray(fname,lst,header=1):
    '''SAVESTRUCTARRAY - Save a structure array into a text file
 
    SAVESTRUCTARRAY(FILENAME, STRUCTARRAY, [HEADER])

    Saves structure array data of type STRUCT into a text
    file.  FILENAME is the name of the file to be written.
    STRUCTARRAY is the Matlab structure to be written (of type
    STRUCT). If HEADER is 1, then a header row is written
    (recommended if the file is to be read back iin with 
    LOADSTRUCTARRAY).  The input argument HEADER is optional 
    (and is 1 if not specified).
 
    Originally by Ken Sugino'''
    try:
        fid=open(fname,'w')
    except Exception:
        print(Exception)
        return 
    if header==1:
        keys=0
        for gdi in lst:
            if keys==0:
                fn=list(gdi.keys())
                s = ''        
                for i in fn:
                    s=s+'\t'+i
                s=s[1:]+'\n'
                keys=1     
            s = s+struct2char(gdi)
    fid.write(s)
    fid.close()