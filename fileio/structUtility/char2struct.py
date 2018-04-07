#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Mar 17 16:52:57 2018

@author: yanglite
"""

def char2struct(s,fields):
    a={}
    if s.endswith('\n'):
        s=s[:-1]
    values=s.split('\t')
    for i in range(len(fields)):
        a.update({fields[i]:values[i]})
    return a