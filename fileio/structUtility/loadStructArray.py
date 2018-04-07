#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Mar 17 15:51:43 2018

@author: yanglite
"""
from char2struct import *
def loadStructArray(fname='',fields=[]):
    # if no fields, get fields from first line
    try:
        fid=open(fname,'r')
    except FileNotFoundError:
        return []
    else:
        a=[]
        if not fields:
            s=fid.readline()
            fields=s[:-1].split('\t')
        for i in fid:
            a.append(char2struct(i,fields))
        fid.close()
        return a
        
