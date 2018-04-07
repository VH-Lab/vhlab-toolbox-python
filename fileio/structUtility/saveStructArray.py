#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr  2 15:09:30 2018

@author: yanglite
"""
from struct2char import *

def saveStructArray(fname,lst,header=1):
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