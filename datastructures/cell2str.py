#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Apr 21 16:15:40 2018

@author: yanglite
"""

def cell2str(lis):
    '''
    CELL2STR - Convert 1-D cells to a string
    
      STR = CELL2STR(THECELL)
    
    Converts a 1-D cell to a string.
    
    Example: 
      A = {'test','test2','test3'};
      str = cell2str(A)
    
          produced str = 
       '{ 'test','test2','test3' }'
    
     1-dim cells only, only chars and matricies
    '''
    if not lis:
        return '[]'
    st='['
    for i in lis:
        st=st+"'"+str(i)+"',"
    st=st[:-1]+']'
    return st