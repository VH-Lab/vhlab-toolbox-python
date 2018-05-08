#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr  4 20:51:56 2018

@author: yanglite
"""

def structmerge(s1, s2, ErrorIfNewField = 0):
    '''
    STRUCTMERGE - Merge struct variables into a common struct
    
     S_OUT = STRUCTMERGE(S1, S2, ...)
    
     Merges the structures S1 and S2 into a common structure S_OUT
     such that S_OUT has all of the fields of S1 and S2. When 
     S1 and S2 share the same fieldname, the value of S2 is taken.
     The fieldnames will be re-ordered to be in alphabetical order.
    
     The behavior of the function can be altered by passing additional
     arguments as name/value pairs. 
    
     Parameter (default)     | Description
     ------------------------------------------------------------
     ErrorIfNewField (0)     | (0/1) Is it an error if S2 contains a
                             |  field that is not present in S1?
    
     See also: STRUCT
    '''    
    f1=list(s1.keys())
    f2=list(s2.keys())
    
    if ErrorIfNewField:
        if set(f2)-set(f1):
            raise Exception('Some fields of the second structure are not in the first'+str(set(f2)-set(f1)))
    s_out=s1
    for i in f2:
        if not s_out:
            s_out={}
        s_out.update({i:s2.get(i)})
    return s_out