#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Mar 17 15:51:43 2018

@author: yanglite
"""

def loadStructArray(fname='/Users/yanglite/Desktop/a.txt',fields=[]):
    # if no fields, get fields from first line
    try:
        a=[]
        fid=open(fname,'r')
    except FileNotFoundError:
        return a
    else:
        if not fields:
            s=fid.readline()
            fields=s.split('\t')
        for i in fid:
            a.append(char2struct(i,fields))
        return a
        fid.close()
            
        