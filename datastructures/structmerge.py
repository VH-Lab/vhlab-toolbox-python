#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr  4 20:51:56 2018

@author: yanglite
"""

def structmerge(s1, s2, *varargin):
    
    #assign(varargin{:})
    
    f1=list(s1.keys())
    f2=list(s2.keys())
    
    s_out=s1
    for i in f2:
        if not s_out:
            s_out={}
        s_out.update({i:s2.get(i)})
    return s_out