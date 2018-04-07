#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr  2 19:19:30 2018

@author: yanglite
"""

def struct2char(a):
    fn=list(a.keys())
    s=''
    for i in fn:
        f=a.get(i)
        s=s+'\t'+str(f)
    return s[1:]+'\n'